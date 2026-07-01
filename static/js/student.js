function toggleStream() {

    const standard = document.getElementById("standard");

    if (!standard) return;

    const streamDiv = document.getElementById("stream_div");
    const stream = document.getElementById("stream");

    const otherStreamDiv = document.getElementById("other_stream_div");
    const otherStream = document.getElementById("other_stream");

    if (
        standard.value === "11th Standard" ||
        standard.value === "12th Standard"
    ) {

        streamDiv.style.display = "block";
        stream.required = true;

        toggleOtherStream();

    }

    else {

        streamDiv.style.display = "none";
        stream.required = false;
        stream.value = "";

        if (otherStreamDiv) {

            otherStreamDiv.style.display = "none";

        }

        if (otherStream) {

            otherStream.required = false;
            otherStream.value = "";

        }

    }

}

function toggleOtherStream() {

    const stream = document.getElementById("stream");

    if (!stream) return;

    const otherStreamDiv = document.getElementById("other_stream_div");
    const otherStream = document.getElementById("other_stream");

    if (!otherStreamDiv || !otherStream) return;

    if (stream.value === "Other") {

        otherStreamDiv.style.display = "block";
        otherStream.required = true;

    }

    else {

        otherStreamDiv.style.display = "none";
        otherStream.required = false;
        otherStream.value = "";

    }

}

document.addEventListener("DOMContentLoaded", function () {

    toggleStream();

    const standard = document.getElementById("standard");

    if (standard) {

        standard.addEventListener(
            "change",
            toggleStream
        );

    }

    const stream = document.getElementById("stream");

    if (stream) {

        stream.addEventListener(
            "change",
            toggleOtherStream
        );

    }

});