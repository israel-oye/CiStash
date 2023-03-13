// import Dropzone from "dropzone";


// Dropzone.options.upload = {
//     paramName: "file",
//     acceptedFiles: ".pdf, .doc, .docx, .odt, .ppt, .pptx",
//     addRemoveLinks: true,
//     chunking: true,
//     forceChunking: true,
//     url: document.querySelector("#upload-url").value,
//     uploadMultiple: false,
//     maxFilesize: 1025, // megabytes
//     chunkSize: 1000000, // bytes
//     dictDefaultMessage: "Upload relevant course document.",
//     dictCancelUpload: "Cancel Upload",
//     dictCancelUploadConfirmation: "Are you sure you want to cancel this upload?",
//     init: function() {
//         this.on('error', function(file, errorMessage) {
//             if (file.accepted) {
//                 var mypreview = document.getElementsByClassName('dz-error');
//                 mypreview = mypreview[mypreview.length - 1];
//                 mypreview.classList.toggle('dz-error');
//                 mypreview.classList.toggle('dz-success');
//             }
//         });
//     },

// }

async function submitForm(formData) {
    try {
        const response = await fetch('/auth/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': formData.get('csrf_token')
            },
            body: JSON.stringify({
                    "csrf_token": formData.get("csrf_token"),
                    "levels": formData.get("levels"),
                    "course_code": formData.get("course_code"),
                    "course_title": formData.get("course_title"),
                })
                // body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.status === 200) {
            const alertString = `<div class="alert  alert-success mt-4 mx-5 text-center fw-bold alert-dismissible fade show" role="alert">
                                    <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#info-fill"/></svg>
                                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                                    <div>
                                        ${data.message}
                                    </div>
                                </div>`

            const parser = new DOMParser();
            const doc = parser.parseFromString(alertString, "text/html");
            const alertElem = doc.querySelector('div')
            const formContainerElem = document.querySelector('#form-container')

            formContainerElem.insertAdjacentElement("beforebegin", alertElem);
        } else if (response.status === 400) {
            //data = resp => {'errors': {'fieldName': [listOfErrors]}}

            //field_errors = {'fieldName': [listOfErrors], 'otherFieldName': [listOfErrors]}
            let field_errors = data.errors

            if (field_errors.hasOwnProperty("course_code")) {
                const courseCodeField_error = field_errors["course_code"][0]

                const courseCodeErrorElem = document.getElementById("course-code-error")
                courseCodeErrorElem.style.display = 'inline';
                courseCodeErrorElem.insertAdjacentText("beforeend", courseCodeField_error)
            }
            if (field_errors.hasOwnProperty("course_title")) {
                const courseTitle_error = field_errors["course_title"][0]

                const courseTitleErrorElem = document.getElementById("course-title-error");
                courseTitleErrorElem.style.display = 'inline';
                courseTitleErrorElem.insertAdjacentText("beforeend", courseTitle_error)
            }
        } else {
            // status = 500
            const alertString = `<div class="alert alert-danger mt-4 mx-5 py-2 text-center fw-bold" role="alert">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2" viewBox="0 0 16 16" role="img" aria-label="Warning:"> <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/> </svg> 
                                    <div>
                                        ${data.message}
                                    </div>
                                </div>`

            const parser = new DOMParser();
            const doc = parser.parseFromString(alertString, "text/html");
            const alertElem = doc.querySelector('div')
            const formContainerElem = doc.querySelector('#form-container')

            formContainerElem.insertAdjacentElement("beforebegin", alertElem);
        }

    } catch (error) {
        console.log(error);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const form_1 = document.getElementById("form1");

    form_1.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(form_1);
        submitForm(formData);
    });
})