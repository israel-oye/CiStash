var parser = new DOMParser();
var alertAnchor = document.querySelector('#alert-anchor');

//Utility function to disable button on File-Upload form
/**
 *
 * @param {boolean} state
 */
function disableUploadButton(state) {
    let button = document.querySelector("#upload-btn");
    if (button && state == true) {
        button.disabled = true;
        button.innerHTML = '<i class="fa-solid fa-arrow-up-from-bracket fa-beat-fade"></i> Uploading'
    } else if (button && state == false) {
        button.disabled = false;
        button.innerHTML = '<i class="fa-solid fa-arrow-up-from-bracket"></i> Upload';
    }
}


//Dropzone Js config

Dropzone.options.upload = {
    paramName: "file",
    acceptedFiles: ".pdf, .doc, .docx, .odt, .rtf, .txt, .epub, .ppt, .pptx",
    addRemoveLinks: true,
    autoProcessQueue: false,
    chunking: true,
    forceChunking: true,
    url: "/resource/file-upload",
    uploadMultiple: false,
    maxFiles: 1,
    maxFilesize: 512, // megabytes
    chunkSize: 1 * 1024 * 1024, // bytes
    retryChunks: false,
    retryChunksLimit: 3,
    dictDefaultMessage: '<h5>Drag file here or click to upload relevant course document. <i style="display: block;" class="fa-solid fa-2x fa-cloud-arrow-up"></i></h5>',
    dictCancelUpload: "Cancel Upload",
    dictCancelUploadConfirmation: "Are you sure you want to cancel this upload?",
    dictUploadCanceled: "Upload canceled.",
    dictResponseError: "Server responded with {{statusCode}} code",
    dictRemoveFile: "Remove",
    init: function() {
        var myDropzone = this;
        var csrfToken = document.querySelector("#upload-token").value;

        this.on('error', function(file, response) {
            if (typeof response === "string") {
                var message = '';
                // Flask aborting an E-500 renders an error page
                if (response.startsWith("<!DOCTYPE html>")) {
                    message = "Something is wrong at the server. Please try again later..."
                } else {
                    message = response;
                }
            } else {
                var message = response.message;
            }
            file.previewElement.classList.add("dz-error");
            _ref = file.previewElement.querySelectorAll("[data-dz-errormessage]");
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                node = _ref[_i];
                _results.push(node.textContent = message);
            }
            disableUploadButton(false);
            return _results;
        });

        this.on('canceled', function(file) {
            disableUploadButton(false);

            var xhr = file.xhr;
            xhr.open('POST', myDropzone.options.url, true);
            xhr.setRequestHeader('X-File-Status', file.status);
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
            xhr.send();

            return myDropzone.emit("error", file, this.options.dictUploadCanceled);
        })

        this.on('sending', function(data, xhr, formData) {
            disableUploadButton(true);
            var selectedCourseId = document.querySelector('#course_code_dropdown');

            xhr.setRequestHeader('X-File-Status', 'uploading');
            formData.append("course_id", selectedCourseId.value);
            formData.append("csrf_token", csrfToken);
        })

        let upload_btn = document.querySelector("#upload-btn");
        upload_btn.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (confirm("Please, press OK if you have selected a relevant course material.") == true) {
                myDropzone.processQueue();
            } else {
                alert("Please select relevant course material for upload.")
            }

        })
    },

    success: function(file, response) {
        disableUploadButton(false);
        show_success_modal("Document uploaded successfully!");
        return file.previewElement.classList.add("dz-success");
    },

    chunksUploaded: function(file, done) {
        done();
    }
}


//Utility functions

/**
 * @param {string} bg_color
 * @param {string} body_content
 */
function construct_alert_element(bg_color, body_content) {

    const alertString = `<div class="alert  alert-${bg_color} mt-4 mx-5 text-center fw-bold alert-dismissible fade show" role="alert">
                            <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#info-fill"/></svg>
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            <div>
                                ${body_content}
                            </div>
                            </div>`

    const doc = parser.parseFromString(alertString, "text/html");
    const alertElem = doc.querySelector('div');

    return alertElem;
}


/**
 * @param {HTMLDivElement} new_alert
 */
function add_alert(new_alert) {
    const alertAnchorSibling = alertAnchor.nextElementSibling;

    if (alertAnchorSibling.role == "alert") {
        alertAnchorSibling.remove();
    }
    alertAnchor.insertAdjacentElement("afterend", new_alert);
}


/**
 *
 * @param {string} modal_text
 */
function show_success_modal(modal_text) {
    const ModalElem = document.querySelector('#success-modal')
    const modal = new bootstrap.Modal(ModalElem);

    document.querySelector("#success-modal-text").innerText = modal_text;
    modal.show();
}


/**
 *
 * @param {string} modal_text
 */
function show_error_modal(modal_text) {
    const ModalElem = document.querySelector('#error-modal')
    const modal = new bootstrap.Modal(ModalElem);

    document.querySelector("#error-modal-text").innerText = modal_text;
    modal.show();
}


/**
 *
 * @param {FormData} formData
 * @param {string} route
 */
async function submitForm(formData, route) {
    try {
        const response = await fetch(route, {
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
            show_success_modal(`${data.message}!`);
        } else if (response.status === 400) {
            //data = resp => {'errors': {'fieldName': [listOfErrors]}}

            //field_errors = {'fieldName': [listOfErrors], 'otherFieldName': [listOfErrors]}
            let field_errors = data.errors

            if (field_errors.hasOwnProperty("course_code")) {
                const courseCodeField_error = field_errors["course_code"][0]

                const courseCodeErrorElem = document.getElementById("course-code-error")
                courseCodeErrorElem.style.display = 'inline';
                const errorSpanElem = courseCodeErrorElem.firstElementChild.nextElementSibling;
                errorSpanElem.innerHTML = courseCodeField_error;
            }
            if (field_errors.hasOwnProperty("course_title")) {
                const courseTitle_error = field_errors["course_title"][0]

                const courseTitleErrorElem = document.getElementById("course-title-error");
                courseTitleErrorElem.style.display = 'inline';
                const errorSpanElem = courseTitleErrorElem.firstElementChild.nextElementSibling;
                errorSpanElem.innerHTML = courseTitle_error;
            }
        } else if (response.status === 401) {
            // Re-Authentication required
            show_error_modal(`${data.message}!`);
        } else if (response.status === 404) {
            //For edit route: Course is not found.
            show_error_modal(`${data.message}!`);
        } else {
            // status = 500
            const alertString = `<div class="alert alert-danger mt-4 mx-5 py-2 text-center fw-bold" role="alert">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-exclamation-triangle-fill flex-shrink-0 me-2" viewBox="0 0 16 16" role="img" aria-label="Warning:"> <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/> </svg>
                                    <div>
                                        ${data.message}
                                    </div>
                                </div>`

            const doc = parser.parseFromString(alertString, "text/html");
            const alertElem = doc.querySelector('div')

            const alertAnchorSibling = alertAnchor.nextElementSibling;
            if (alertAnchorSibling.classList.contains("alert")) {
                alertAnchorSibling.remove();
            }
            alertAnchor.insertAdjacentElement("afterend", alertElem);
        }

    } catch (error) {
        console.log(error);
        show_error_modal(`An error occured while sending. Please try again.`);
    }
}

async function get_level_courses(level_name) {
    try {
        const response = await fetch(`/resource/fetch/${level_name}/courses`);

        let data = await response.json();

        const optionArray = [];
        for (let course of data.courses) {
            var optionElem = document.createElement('option');
            optionElem.value = course.id;
            optionElem.innerHTML = course.course_code;
            optionArray.push(optionElem);
        }

        return optionArray;

    } catch (error) {
        console.error(error);
    }
}


let form_2_level_select = document.querySelector("#form2-level");
let course_code_select = document.querySelector("#course_code_dropdown");

document.addEventListener("DOMContentLoaded", function() {
    const addCourseForm = document.getElementById("add-course-form");

    if (addCourseForm) {
        var courseButton = document.getElementById("add-course-btn");
        var courseCodeErrorElem = document.getElementById("course-code-error");
        var courseTitleErrorElem = document.getElementById("course-title-error");

        courseButton.addEventListener('click', function(e) {
            courseCodeErrorElem.style.display = "none";
            courseTitleErrorElem.style.display = "none";
        })

        addCourseForm.addEventListener('submit', (event) => {
            courseButton.disabled = true;
            courseButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding Course'
            event.preventDefault();
            const formData = new FormData(addCourseForm);
            submitForm(formData, `/resource/add-course`)
                .then(() => {
                    setTimeout(function() {
                        courseButton.disabled = false;
                        courseButton.innerHTML = '<i class="fa-regular fa-square-plus"></i> Add Course'
                    }, 500)
                })
                .catch(error => {
                    console.error('An error occurred:', error);
                });
        });
    }


    const editCourseForm = document.getElementById("edit-course-form");

    if (editCourseForm) {
        var courseButton = document.getElementById("edit-course-btn");
        var courseCodeErrorElem = document.getElementById("course-code-error");
        var courseTitleErrorElem = document.getElementById("course-title-error");
        var courseId = '';

        courseButton.addEventListener('click', function(e) {

            courseCodeErrorElem.style.display = "none";
            courseTitleErrorElem.style.display = "none";
            courseId = this.value;
        })

        editCourseForm.addEventListener('submit', (event) => {
            courseButton.disabled = true;
            courseButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating'
            event.preventDefault();
            const formData = new FormData(editCourseForm);
            submitForm(formData, `/resource/edit-course/${courseId}`)
                .then(() => {
                    setTimeout(function() {
                        courseButton.disabled = false;
                        courseButton.innerHTML = '<i class="fa-solid fa-pen-to-square"></i></i> Update Course'
                    }, 1500)
                })
                .catch(error => {
                    console.error(error);
                });
        });

    }
})


//UPDATING Course-Code dropwdown (in File upload form) DYNAMICALLY AS Level dropdown changes

if (form_2_level_select) {
    let form_2_tab_btn = document.getElementById("document-tab");

    form_2_tab_btn.addEventListener('click', function(e) {
        let selected_level = form_2_level_select.value;
        course_code_select.innerHTML = "";

        get_level_courses(selected_level).
        then((optionArray) => {
            var updated_options = optionArray;

            for (let option of updated_options) {
                course_code_select.appendChild(option);
            }
        })

    })

    form_2_level_select.addEventListener('change', function(e) {
        let selected_level = form_2_level_select.value;
        course_code_select.innerHTML = "";

        get_level_courses(selected_level).
        then((optionArray) => {
            var updated_options = optionArray;

            for (option of updated_options) {
                course_code_select.appendChild(option);
            }
        })

    });
}


//REFRESH WINDOW ON RESPECTIVE MODAL DISMISSAL

let add_file_dialog = document.getElementById("add-file-modal")

if (add_file_dialog) {
    add_file_dialog.addEventListener('hidden.bs.modal', function(e) {
        window.location = window.location;
    })
}


let edit_file_dialog = document.getElementById("edit-course-modal");

if (edit_file_dialog) {
    edit_file_dialog.addEventListener('hidden.bs.modal', function(e) {
        window.location = window.location;
    })
}


let add_course_dialog = document.getElementById("add-course-modal");

if (add_course_dialog) {
    add_course_dialog.addEventListener('hidden.bs.modal', function(e) {
        window.location = window.location;
    })
}