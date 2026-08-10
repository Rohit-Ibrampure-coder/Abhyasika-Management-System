from calendar import month_name
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request
)

from flask_login import (
    login_required
)

from models.achievement import Achievement
from models.remark import Remark
from models.student_evaluation import StudentEvaluation
from models.abhyasika import Abhyasika
from sqlalchemy import func
from collections import defaultdict
from models.student import Student
from sqlalchemy import or_
from models.attendance import Attendance
from models.attendance_session import AttendanceSession
from models.student_evaluation_answer import StudentEvaluationAnswer
from models.student_evaluation_question import StudentEvaluationQuestion
from models.student_evaluation_question_group import StudentEvaluationQuestionGroup

student_evaluation_report_bp = Blueprint(
    "student_evaluation_report",
    __name__
)


# ==========================================
# Student Progress & Evaluation Report Home
# ==========================================

@student_evaluation_report_bp.route(
    "/student-evaluation-report"
)
@login_required
def report_home():

    search = request.args.get(
        "search",
        ""
    )

    query = Student.query

    if search:

        query = query.filter(

            or_(

                Student.student_name.ilike(
                    f"%{search}%"
                ),

                Student.parent_name.ilike(
                    f"%{search}%"
                )

            )

        )

    students = query.order_by(

        Student.student_name

    ).all()

    report_students = []

    for student in students:

        total_evaluations = StudentEvaluation.query.filter_by(
            student_id=student.id
        ).count()

        last_evaluation = StudentEvaluation.query.filter_by(
            student_id=student.id
        ).order_by(
            StudentEvaluation.evaluation_date.desc()
        ).first()

        report_students.append({

            "student": student,

            "abhyasika": student.abhyasika.name
            if student.abhyasika else "-",

            "total_evaluations": total_evaluations,

            "last_evaluation": (
                last_evaluation.evaluation_date
                if last_evaluation else None
            )

        })

    return render_template(

        "evaluation/student_report/report_home.html",

        report_students=report_students,

        search=search

    )

# ==========================================
# Academic Year Helper
# ==========================================

ACADEMIC_YEAR_START_MONTH = 6


def get_academic_year(target_date):

    year = target_date.year

    if target_date.month >= ACADEMIC_YEAR_START_MONTH:

        start_year = year

    else:

        start_year = year - 1

    end_year = start_year + 1

    return (
        f"{start_year}-{str(end_year)[-2:]}"
    )

# ==========================================
# Student Progress Report
# ==========================================

@student_evaluation_report_bp.route(
    "/student-evaluation-report/<int:student_id>"
)
@login_required
def student_progress_report(student_id):

    student = Student.query.get_or_404(student_id)

    # ==========================================
    # Attendance Information
    # Year → Month scalable structure
    # ==========================================

    attendance_records = (
        Attendance.query
        .join(
            AttendanceSession,
            Attendance.attendance_session_id ==
            AttendanceSession.id
        )
        .filter(
            Attendance.student_id == student.id
        )
        .all()
    )


    attendance_year_data = defaultdict(
        lambda: {
            "present": 0,
            "absent": 0,
            "total": 0,
            "months": defaultdict(
                lambda: {
                    "present": 0,
                    "absent": 0,
                    "total": 0
                }
            )
        }
    )


    for attendance in attendance_records:

        attendance_date = (
            attendance.attendance_session.attendance_date
        )

        academic_year = get_academic_year(
            attendance_date
        )

        month_key = attendance_date.strftime(
            "%Y-%m"
        )

        month_name = attendance_date.strftime(
            "%B"
        )

        # ==========================================
        # Year totals
        # ==========================================

        attendance_year_data[
            academic_year
        ]["total"] += 1

        # ==========================================
        # Month totals
        # ==========================================

        attendance_year_data[
            academic_year
        ]["months"][month_key]["total"] += 1

        if attendance.status == "Present":

            attendance_year_data[
                academic_year
            ]["present"] += 1

            attendance_year_data[
                academic_year
            ]["months"][month_key]["present"] += 1

        elif attendance.status == "Absent":

            attendance_year_data[
                academic_year
            ]["absent"] += 1

            attendance_year_data[
                academic_year
            ]["months"][month_key]["absent"] += 1

    # ==========================================
    # Prepare Attendance Year Summary
    # ==========================================

    attendance_year_summary = []

    for academic_year in sorted(
        attendance_year_data.keys()
    ):

        year_data = attendance_year_data[
            academic_year
        ]

        total = year_data["total"]

        if total > 0:

            percentage = round(
                (
                    year_data["present"] /
                    total
                ) * 100,
                2
            )

        else:

            percentage = 0.00

        year_months = []

        for month_key in sorted(
            year_data["months"].keys()
        ):

            month_data = year_data[
                "months"
            ][month_key]

            month_total = month_data["total"]

            if month_total > 0:

                month_percentage = round(
                    (
                        month_data["present"] /
                        month_total
                    ) * 100,
                    2
                )

            else:

                month_percentage = 0.00

            month_date = datetime.strptime(
                month_key,
                "%Y-%m"
            )


            # ==========================================
            # Month-wise Change
            # ==========================================

            if len(year_months) == 0:

                month_change = None

            else:

                previous_month_percentage = (
                    year_months[-1]["percentage"]
                )

                month_change = round(
                    month_percentage -
                    previous_month_percentage,
                    2
                )


            # ==========================================
            # Store Month Summary
            # ==========================================

            year_months.append({

                "month_key": month_key,

                "month": month_date.strftime(
                    "%B"
                ),

                "present": month_data[
                    "present"
                ],

                "absent": month_data[
                    "absent"
                ],

                "total": month_total,

                "percentage": month_percentage,

                "change": month_change

            })

        attendance_year_summary.append({

            "academic_year": academic_year,

            "present": year_data[
                "present"
            ],

            "absent": year_data[
                "absent"
            ],

            "total": total,

            "percentage": percentage,

            "months": year_months

        })

    # ==========================================
    # Overall Attendance
    # Entire Abhyasika Period
    # ==========================================

    overall_present_days = sum(
        item["present"]
        for item in attendance_year_summary
    )

    overall_absent_days = sum(
        item["absent"]
        for item in attendance_year_summary
    )

    overall_attendance_days = (
        overall_present_days +
        overall_absent_days
    )

    if overall_attendance_days > 0:

        overall_attendance_percentage = round(
            (
                overall_present_days /
                overall_attendance_days
            ) * 100,
            2
        )

    else:

        overall_attendance_percentage = 0.00    

    # ==========================================
    # Student Achievements
    # ==========================================

    achievements = (
        Achievement.query
        .filter_by(
            student_id=student.id
        )
        .order_by(
            Achievement.achievement_date.desc(),
            Achievement.created_at.desc()
        )
        .all()
    )

    # ==========================================
    # Teacher Remarks
    # ==========================================

    teacher_remarks = (
        Remark.query
        .filter_by(
            student_id=student.id
        )
        .order_by(
            Remark.created_at.desc()
        )
        .all()
    )

    # ==========================================
    # Group Remarks By Teacher
    # ==========================================

    grouped_teacher_remarks = {}

    for remark in teacher_remarks:

        if remark.teacher_id not in grouped_teacher_remarks:

            grouped_teacher_remarks[
                remark.teacher_id
            ] = {

                "teacher": remark.teacher,

                "remarks": []

            }

        grouped_teacher_remarks[
            remark.teacher_id
        ]["remarks"].append(
            remark
        )

    evaluations = StudentEvaluation.query.filter_by(

        student_id=student.id

    ).order_by(

        StudentEvaluation.evaluation_date.asc()

    ).all()

    # ==========================================
    # Progress Summary
    # ==========================================

    total_evaluations = len(evaluations)

    average_percentage = 0.00
    best_percentage = 0.00
    latest_percentage = 0.00

    percentages = []

    for evaluation in evaluations:

        if evaluation.result:

            percentages.append(

                float(
                    evaluation.result.percentage
                )

            )

    if percentages:

        average_percentage = round(

            sum(percentages) / len(percentages),

            2

        )

        best_percentage = max(percentages)

    if evaluations:

        latest_result = evaluations[-1].result

        if latest_result:

            latest_percentage = float(

                latest_result.percentage

            )

    first_evaluation = None
    last_evaluation = None

    if evaluations:

        first_evaluation = evaluations[0]

        last_evaluation = evaluations[-1]


    # ==========================================
    # Evaluation Year → Month Structure
    # ==========================================

    evaluation_year_data = defaultdict(
        lambda: {
            "evaluation_count": 0,
            "obtained_marks": 0,
            "total_marks": 0,
            "months": defaultdict(
                lambda: {
                    "evaluation_count": 0,
                    "obtained_marks": 0,
                    "total_marks": 0,
                    "evaluations": []
                }
            )
        }
    )


    for evaluation in evaluations:

        if not evaluation.result:

            continue

        evaluation_date = (
            evaluation.evaluation_date
        )

        academic_year = get_academic_year(
            evaluation_date
        )

        month_key = evaluation_date.strftime(
            "%Y-%m"
        )

        # ==========================================
        # Academic Year Totals
        # ==========================================

        evaluation_year_data[
            academic_year
        ]["evaluation_count"] += 1

        evaluation_year_data[
            academic_year
        ]["obtained_marks"] += (
            evaluation.result.obtained_marks
        )

        evaluation_year_data[
            academic_year
        ]["total_marks"] += (
            evaluation.result.total_questions
        )

        # ==========================================
        # Month Totals
        # ==========================================

        evaluation_year_data[
            academic_year
        ]["months"][month_key][
            "evaluation_count"
        ] += 1

        evaluation_year_data[
            academic_year
        ]["months"][month_key][
            "obtained_marks"
        ] += (
            evaluation.result.obtained_marks
        )

        evaluation_year_data[
            academic_year
        ]["months"][month_key][
            "total_marks"
        ] += (
            evaluation.result.total_questions
        )

        evaluation_year_data[
            academic_year
        ]["months"][month_key][
            "evaluations"
        ].append(
            evaluation
        )

    # ==========================================
    # Prepare Evaluation Year Summary
    # ==========================================

    evaluation_year_summary = []

    for academic_year in sorted(
        evaluation_year_data.keys()
    ):

        year_data = evaluation_year_data[
            academic_year
        ]

        obtained = year_data[
            "obtained_marks"
        ]

        total = year_data[
            "total_marks"
        ]

        if total > 0:

            percentage = round(
                (
                    obtained /
                    total
                ) * 100,
                2
            )

        else:

            percentage = 0.00

        year_months = []

        for month_key in sorted(
            year_data["months"].keys()
        ):

            month_data = year_data[
                "months"
            ][month_key]

            month_obtained = month_data[
                "obtained_marks"
            ]

            month_total = month_data[
                "total_marks"
            ]

            if month_total > 0:

                month_percentage = round(
                    (
                        month_obtained /
                        month_total
                    ) * 100,
                    2
                )

            else:

                month_percentage = 0.00

            month_date = datetime.strptime(
                month_key,
                "%Y-%m"
            )

            # ==========================================
            # Month-wise Change
            # ==========================================

            if len(year_months) == 0:

                month_change = None

            else:

                previous_month_percentage = (
                    year_months[-1]["percentage"]
                )

                month_change = round(
                    month_percentage -
                    previous_month_percentage,
                    2
                )

            year_months.append({

                "month_key": month_key,

                "month": month_date.strftime(
                    "%B"
                ),

                "evaluation_count":
                    month_data[
                        "evaluation_count"
                    ],

                "obtained_marks":
                    month_obtained,

                "total_marks":
                    month_total,

                "percentage":
                    month_percentage,

                "change": month_change,

                "evaluations":
                    month_data[
                        "evaluations"
                    ]

            })

        evaluation_year_summary.append({

            "academic_year": academic_year,

            "evaluation_count":
                year_data[
                    "evaluation_count"
                ],

            "obtained_marks":
                obtained,

            "total_marks":
                total,

            "percentage":
                percentage,

            "months":
                year_months

        })

    # ==========================================
    # Academic Year Growth
    # ==========================================

    previous_percentage = None

    for year_data in evaluation_year_summary:

        if previous_percentage is None:

            year_data["change"] = None

        else:

            year_data["change"] = round(
                year_data["percentage"] -
                previous_percentage,
                2
            )

        previous_percentage = (
            year_data["percentage"]
        )
   
    # ==========================================
    # Adaptive Chart Data
    # ==========================================

    chart_labels = []
    chart_percentages = []
    chart_obtained_marks = []
    chart_total_questions = []

    # ------------------------------------------
    # Show Every Evaluation (12 or fewer)
    # ------------------------------------------

    if len(evaluations) <= 12:

        for evaluation in evaluations:

            if evaluation.result:

                chart_labels.append(

                    evaluation.evaluation_date.strftime(

                        "%d-%m-%Y"

                    )

                )

                chart_percentages.append(

                    float(

                        evaluation.result.percentage

                    )

                )

                chart_obtained_marks.append(

                    evaluation.result.obtained_marks

                )

                chart_total_questions.append(

                    evaluation.result.total_questions

                )

    # ------------------------------------------
    # Monthly Average (More than 12)
    # ------------------------------------------

    else:

        monthly_data = defaultdict(list)

        monthly_marks = defaultdict(list)

        monthly_totals = defaultdict(list)

        for evaluation in evaluations:

            if evaluation.result:

                month = evaluation.evaluation_date.strftime(

                    "%b %Y"

                )

                monthly_data[month].append(

                    float(

                        evaluation.result.percentage

                    )

                )

                monthly_marks[month].append(

                    evaluation.result.obtained_marks

                )

                monthly_totals[month].append(

                    evaluation.result.total_questions

                )

        for month in monthly_data:

            chart_labels.append(month)

            chart_percentages.append(

                round(

                    sum(monthly_data[month]) /

                    len(monthly_data[month]),

                    2

                )

            )

            chart_obtained_marks.append(

                round(

                    sum(monthly_marks[month]) /

                    len(monthly_marks[month]),

                    1

                )

            )

            chart_total_questions.append(

                round(

                    sum(monthly_totals[month]) /

                    len(monthly_totals[month]),

                    1

                )

            )

    # ==========================================
    # Graph Insights
    # ==========================================

    highest_percentage = 0

    lowest_percentage = 0

    overall_improvement = 0

    performance_status = "माहिती उपलब्ध नाही"

    if percentages:

        highest_percentage = max(percentages)

        lowest_percentage = min(percentages)

        if len(percentages) >= 2:

            overall_improvement = round(

                percentages[-1] - percentages[0],

                2

            )

        if average_percentage >= 90:

            performance_status = "उत्कृष्ट"

        elif average_percentage >= 75:

            performance_status = "खूप चांगली प्रगती"

        elif average_percentage >= 60:

            performance_status = "सुधारणा होत आहे"

        elif average_percentage >= 40:

            performance_status = "लक्ष आवश्यक"

        else:

            performance_status = "तात्काळ लक्ष आवश्यक"

    # ==========================================
    # Automatic Observation
    # ==========================================

    observation_title = ""

    observation_message = ""

    if total_evaluations == 0:

        observation_title = "माहिती उपलब्ध नाही"

        observation_message = (

            "विद्यार्थ्याचे अद्याप कोणतेही मूल्यांकन झालेले नाही."

        )

    elif overall_improvement >= 20:

        observation_title = "उत्कृष्ट प्रगती"

        observation_message = (

            "विद्यार्थ्याच्या कामगिरीमध्ये सातत्याने मोठी सुधारणा दिसून येत आहे. "

            "ही प्रगती कायम ठेवण्यासाठी नियमित मार्गदर्शन सुरू ठेवावे."

        )

    elif overall_improvement >= 10:

        observation_title = "चांगली प्रगती"

        observation_message = (

            "विद्यार्थ्याची कामगिरी हळूहळू सुधारत आहे. "

            "नियमित सराव व प्रोत्साहन सुरू ठेवावे."

        )

    elif overall_improvement >= 0:

        observation_title = "स्थिर प्रगती"

        observation_message = (

            "विद्यार्थ्याची कामगिरी स्थिर आहे. "

            "अधिक प्रगतीसाठी काही बाबींवर विशेष लक्ष देण्याची आवश्यकता आहे."

        )

    else:

        observation_title = "सुधारणा आवश्यक"

        observation_message = (

            "विद्यार्थ्याच्या कामगिरीमध्ये घट दिसून येत आहे. "

            "शिक्षकांनी व पालकांनी नियमित मार्गदर्शन करणे आवश्यक आहे."

        )

    # ==========================================
    # Student Improvement Trend
    # ==========================================

    trend_status = "No Data"

    trend_color = "secondary"

    latest_change = 0.0

    average_change = 0.0

    consistency = 0

    changes = []

    if len(chart_percentages) >= 2:

        for i in range(

            1,

            len(chart_percentages)

        ):

            change = (

                chart_percentages[i] -

                chart_percentages[i - 1]

            )

            changes.append(change)

        latest_change = round(

            changes[-1],

            2

        )

        average_change = round(

            sum(changes) /

            len(changes),

            2

        )

        # --------------------------------------
        # Overall Trend
        # --------------------------------------

        trend_title = ""

        trend_message = ""

        if average_change >= 5:

            trend_status = "success"

            trend_title = "उत्कृष्ट प्रगती"

            trend_message = (

                "विद्यार्थ्याच्या कामगिरीमध्ये सातत्याने उत्कृष्ट सुधारणा होत आहे."

            )

        elif average_change >= 1:

            trend_status = "primary"

            trend_title = "सातत्यपूर्ण प्रगती"

            trend_message = (

                "विद्यार्थ्याची प्रगती योग्य दिशेने सुरू आहे."

            )

        elif average_change > -1:

            trend_status = "warning"

            trend_title = "स्थिर प्रगती"

            trend_message = (

                "विद्यार्थ्याची कामगिरी स्थिर आहे."

            )

        else:

            trend_status = "danger"

            trend_title = "विशेष लक्ष आवश्यक"

            trend_message = (

                "विद्यार्थ्याच्या कामगिरीमध्ये घट दिसून येत आहे."

            )

        trend_color = trend_status

        # --------------------------------------
        # Consistency
        # --------------------------------------

        positive = len(

            [

                x

                for x in changes

                if x >= 0

            ]

        )

        consistency = round(

            (

                positive /

                len(changes)

            ) * 100

        )

    # ==========================================
    # Core Question Analysis
    # ==========================================

    from models.student_evaluation_question import StudentEvaluationQuestion

    from models.student_evaluation_answer import StudentEvaluationAnswer

    from models.student_evaluation_question_group import StudentEvaluationQuestionGroup

    core_question_summary = []

    core_questions = (

        StudentEvaluationQuestion.query

        .join(StudentEvaluationQuestionGroup)

        .filter(

            StudentEvaluationQuestionGroup.group_type == "Core",

            StudentEvaluationQuestion.is_active == True

        )

        .order_by(

            StudentEvaluationQuestion.display_order

        )

        .all()

    )

    for question in core_questions:

        answers = (

            StudentEvaluationAnswer.query

            .join(StudentEvaluation)

            .filter(

                StudentEvaluation.student_id == student.id,

                StudentEvaluationAnswer.question_id == question.id

            )

            .all()

        )

        yes_count = sum(

            1

            for answer in answers

            if answer.answer

        )

        no_count = len(answers) - yes_count

        total_answers = len(answers)

        if total_answers > 0:

            percentage = round(

                (yes_count / total_answers) * 100,

                2

            )

        else:

            percentage = 0

        # ==========================================
        # Status
        # ==========================================

        if percentage >= 90:

            status = "उत्कृष्ट"

            status_color = "success"

        elif percentage >= 75:

            status = "खूप चांगली प्रगती"

            status_color = "primary"

        elif percentage >= 60:

            status = "सुधारणा होत आहे"

            status_color = "warning"

        elif percentage >= 40:

            status = "लक्ष आवश्यक"

            status_color = "secondary"

        else:

            status = "तात्काळ लक्ष आवश्यक"

            status_color = "danger"

        # ==========================================
        # Save Summary
        # ==========================================

        core_question_summary.append(

            {

                "question": question,

                "yes_count": yes_count,

                "no_count": no_count,

                "total_answers": total_answers,

                "percentage": percentage,

                "status": status,

                "status_color": status_color

            }

        )
    
    # ==========================================
    # Student Strengths & Needs Improvement
    # ==========================================

    student_strengths = []

    needs_improvement = []

    for item in core_question_summary:

        if item["percentage"] >= 80:

            student_strengths.append(item)

        elif item["percentage"] < 60:

            needs_improvement.append(item)

    student_strengths.sort(

        key=lambda x: x["percentage"],

        reverse=True

    )

    needs_improvement.sort(

        key=lambda x: x["percentage"]

    )

    # ==========================================
    # Latest Evaluation Comparison
    # ==========================================

    latest_changes = []

    if len(evaluations) >= 2:

        previous_evaluation = evaluations[-2]

        latest_evaluation = evaluations[-1]

        previous_answers = {

            answer.question_id: answer.answer

            for answer in previous_evaluation.evaluation_answers

        }

        latest_answers = {

            answer.question_id: answer.answer

            for answer in latest_evaluation.evaluation_answers

        }

        for question in core_questions:

            previous = previous_answers.get(question.id)

            current = latest_answers.get(question.id)

            if previous is None or current is None:

                continue

            if previous == False and current == True:

                trend = "improved"

                trend_text = "सुधारणा"

                trend_icon = "bi-arrow-up-circle-fill"

                trend_color = "success"

            elif previous == True and current == False:

                trend = "declined"

                trend_text = "घट"

                trend_icon = "bi-arrow-down-circle-fill"

                trend_color = "danger"

            else:

                trend = "same"

                trend_text = "बदल नाही"

                trend_icon = "bi-dash-circle-fill"

                trend_color = "secondary"

            latest_changes.append({

                "question": question.question_text,

                "previous": previous,

                "current": current,

                "trend": trend,

                "trend_text": trend_text,

                "trend_icon": trend_icon,

                "trend_color": trend_color

            })

    # ==========================================
    # Comparison Summary
    # ==========================================

    improved_count = sum(

        1

        for item in latest_changes

        if item["trend"] == "improved"

    )

    same_count = sum(

        1

        for item in latest_changes

        if item["trend"] == "same"

    )

    declined_count = sum(

        1

        for item in latest_changes

        if item["trend"] == "declined"

    )

    # ==========================================
    # Evaluation History
    # ==========================================

    evaluation_history = []

    for evaluation in reversed(evaluations):

        result = evaluation.result

        # --------------------------------------
        # Default Values
        # --------------------------------------

        obtained_marks = 0

        total_questions = 0

        percentage = 0.00

        if result:

            obtained_marks = result.obtained_marks

            total_questions = result.total_questions

            percentage = float(

                result.percentage

            )

        # --------------------------------------
        # Status
        # --------------------------------------

        if percentage >= 90:

            status = "उत्कृष्ट"

            status_color = "success"

        elif percentage >= 75:

            status = "खूप चांगले"

            status_color = "primary"

        elif percentage >= 60:

            status = "चांगली प्रगती"

            status_color = "warning"

        else:

            status = "सुधारणा आवश्यक"

            status_color = "danger"

        # --------------------------------------
        # Save
        # --------------------------------------

        evaluation_history.append(

            {

                "id": evaluation.id,

                "date": evaluation.evaluation_date,

                "teacher": evaluation.teacher.name,

                "obtained_marks": obtained_marks,

                "total_questions": total_questions,

                "percentage": percentage,

                "status": status,

                "status_color": status_color

            }

        )

    return render_template(

        "evaluation/student_report/student_progress_report.html",

        student=student,

        evaluations=evaluations,

        first_evaluation=first_evaluation,

        last_evaluation=last_evaluation,

        total_evaluations=total_evaluations,

        average_percentage=average_percentage,

        best_percentage=best_percentage,

        latest_percentage=latest_percentage,

        chart_labels=chart_labels,

        chart_percentages=chart_percentages,

        chart_obtained_marks=chart_obtained_marks,

        chart_total_questions=chart_total_questions,

        core_question_summary=core_question_summary,

        highest_percentage=highest_percentage,

        lowest_percentage=lowest_percentage,

        overall_improvement=overall_improvement,

        performance_status=performance_status,

        observation_title=observation_title,

        observation_message=observation_message,

        student_strengths=student_strengths,

        needs_improvement=needs_improvement,

        latest_changes=latest_changes,

        improved_count=improved_count,

        same_count=same_count,

        declined_count=declined_count,

        evaluation_history=evaluation_history,

        trend_status=trend_status,

        trend_color=trend_color,

        latest_change=latest_change,

        average_change=average_change,

        consistency=consistency,

        trend_title=trend_title,

        trend_message=trend_message,

        achievements=achievements,

        grouped_teacher_remarks=grouped_teacher_remarks,

        teacher_remarks=teacher_remarks,

        # ==========================================
        # Scalable Attendance
        # ==========================================

        attendance_year_summary=attendance_year_summary,

        overall_present_days=overall_present_days,

        overall_absent_days=overall_absent_days,

        overall_attendance_days=overall_attendance_days,

        overall_attendance_percentage=
            overall_attendance_percentage,

        # ==========================================
        # Scalable Evaluation
        # ==========================================

        evaluation_year_summary=
            evaluation_year_summary

    )


# ==========================================
# Detailed Question-wise Performance
# ==========================================

@student_evaluation_report_bp.route(
    "/student-evaluation-report/<int:student_id>/question-details"
)
@login_required
def student_question_details(student_id):

    student = Student.query.get_or_404(
        student_id
    )

    # ==========================================
    # Get all evaluations
    # ==========================================

    evaluations = (
        StudentEvaluation.query
        .filter_by(
            student_id=student.id
        )
        .order_by(
            StudentEvaluation.evaluation_date.asc()
        )
        .all()
    )

    # ==========================================
    # Core Questions
    # ==========================================

    core_group = (
        StudentEvaluationQuestionGroup.query
        .filter_by(
            group_name="Core",
            is_active=True
        )
        .first()
    )

    core_questions = []

    if core_group:

        core_questions = (
            StudentEvaluationQuestion.query
            .filter_by(
                question_group_id=core_group.id,
                is_active=True
            )
            .order_by(
                StudentEvaluationQuestion.display_order
            )
            .all()
        )

    # ==========================================
    # Core Question Counts
    # ==========================================

    core_question_counts = {}

    for question in core_questions:

        yes_count = 0

        no_count = 0

        for evaluation in evaluations:

            answer = (
                StudentEvaluationAnswer.query
                .filter_by(
                    evaluation_id=evaluation.id,
                    question_id=question.id
                )
                .first()
            )

            if answer:

                if answer.answer:

                    yes_count += 1

                else:

                    no_count += 1

        # ==========================================
        # Total Evaluated
        # ==========================================

        total_answers = (
            yes_count + no_count
        )

        # ==========================================
        # Marks
        # ==========================================
        # होय = 1 गुण
        # नाही = 0 गुण
        # ==========================================

        obtained_marks = yes_count

        total_marks = total_answers

        # ==========================================
        # Performance Percentage
        # ==========================================

        if total_marks > 0:

            percentage = round(
                (
                    obtained_marks /
                    total_marks
                ) * 100,
                2
            )

        else:

            percentage = 0.00

        # ==========================================
        # Save Question Summary
        # ==========================================

        core_question_counts[
            question.id
        ] = {

            "yes": yes_count,

            "no": no_count,

            "total": total_answers,

            "obtained_marks":
                obtained_marks,

            "total_marks":
                total_marks,

            "percentage":
                percentage

        }

    # ==========================================
    # Evaluation Details
    # ==========================================

    evaluation_details = []

    for evaluation in evaluations:

        answers = (
            StudentEvaluationAnswer.query
            .filter_by(
                evaluation_id=evaluation.id
            )
            .all()
        )

        answer_dict = {
            answer.question_id: answer.answer
            for answer in answers
        }

        current_month = month_name[
            evaluation.evaluation_date.month
        ]

        month_group = (
            StudentEvaluationQuestionGroup.query
            .filter_by(
                group_name=current_month,
                is_active=True
            )
            .first()
        )

        month_questions = []

        if month_group:

            month_questions = (
                StudentEvaluationQuestion.query
                .filter_by(
                    question_group_id=month_group.id,
                    is_active=True
                )
                .order_by(
                    StudentEvaluationQuestion.display_order
                )
                .all()
            )

        evaluation_details.append({

            "evaluation": evaluation,

            "answer_dict": answer_dict,

            "current_month": current_month,

            "month_questions": month_questions

        })

    # ==========================================
    # Group Evaluations by Academic Year
    # ==========================================

    evaluation_years = {}

    for item in evaluation_details:

        evaluation = item["evaluation"]

        evaluation_date = evaluation.evaluation_date

        year = evaluation_date.year

        month = evaluation_date.month

        # Academic year starts in June
        if month >= 6:

            academic_year = (
                f"{year}-{str(year + 1)[-2:]}"
            )

        else:

            academic_year = (
                f"{year - 1}-{str(year)[-2:]}"
            )

        if academic_year not in evaluation_years:

            evaluation_years[academic_year] = []

        evaluation_years[
            academic_year
        ].append(item)

    return render_template(

        "evaluation/student_report/"
        "student_question_details.html",

        student=student,

        core_questions=core_questions,

        core_question_counts=
            core_question_counts,

        evaluation_details=
            evaluation_details,

        evaluation_years=
            evaluation_years

    )