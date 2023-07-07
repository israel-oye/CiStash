const alertAnchor = document.querySelector('#alert-anchor');
const parser = new DOMParser();


/**
 * @param {HTMLDivElement} new_alert
 */
function add_alert(new_alert) {
    const alertAnchorSibling = alertAnchor.nextElementSibling;

    if (alertAnchorSibling.role == "alert") {
        alertAnchorSibling.remove();
    }
    alertAnchor.insertAdjacentElement("afterend", new_alert);

    var toastElement = document.querySelector('.toast');
    var toast = new bootstrap.Toast(toastElement);
    toast.show();
}

/**
 *
 * @param {string} bg_color
 * @param {string} header_content
 * @param {string} body_content
 */
function construct_alert_element(bg_color, header_content, body_content) {
    const alertString = `<div class="toast ms-auto me-3 mt-3 bg-${bg_color} bg-gradient text-light fade show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay=20000>
                                <div class="toast-header bg-${bg_color} text-light">
                                    <strong class="me-auto">${header_content}</strong>
                                    <small>Now</small>
                                    <button type="button" class="btn-close ms-2 mb-1" data-bs-dismiss="toast" aria-label="Close"><span aria-hidden="true"></span>
                                    </button>
                                </div>
                                <div class="toast-body">
                                    ${body_content}
                                </div>
                            </div>`

    const doc = parser.parseFromString(alertString, "text/html");
    const alertElem = doc.querySelector('div');

    return alertElem;
}


async function downloadFile(file_uuid) {
    try {
        const download_url = `/resource/document/${file_uuid}/download`

        const response = await fetch(download_url);

        if (response.status == 200) {

            const contentDisposition = response.headers.get('Content-Disposition');
            const fileNameMatch = contentDisposition.match(/filename=([^;]+)/i);
            const fileName = fileNameMatch ? fileNameMatch[1] : 'file';

            const blob = await response.blob();

            const a = document.createElement('a');
            const url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = fileName;
            a.click();

            let alert_header_content = `<i class="fa-solid fa-square-check"></i> Success`
            let alert_body_text = `Downloaded successfuly!`
            const alertElem = construct_alert_element("success", alert_header_content, alert_body_text);

            add_alert(alertElem);

            window.URL.revokeObjectURL(url);

        } else if (response.status == 400) {

            let alert_header_content = `<i class="fa-solid fa-circle-exclamation fa-bounce"></i> Error`
            let alert_body_text = `The requested resource does not exist...`
            const alertElem = construct_alert_element("warning", alert_header_content, alert_body_text);

            add_alert(alertElem)
        } else {
            let alert_header_content = `<i class="fa-solid fa-circle-exclamation fa-bounce"></i> Error`
            let alert_body_text = `An error occured while downloading...Please try again`
            const alertElem = construct_alert_element("warning", alert_header_content, alert_body_text);

            add_alert(alertElem)
        }

    } catch (error) {
        console.error(error);
    }
}


const downloaders = document.querySelectorAll(".downloader");
if (downloaders.length > 0) {
    let alert_header_content = `<i class="fa-solid fa-download fa-bounce"></i> Downloading`
    let alert_body_message = `Please wait, your download will begin shortly...`
    const alertElem = construct_alert_element("info", alert_header_content, alert_body_message)

    downloaders.forEach(button => {
        button.addEventListener("click", function() {
            add_alert(alertElem);
            const file_uuid = button.value;
            downloadFile(file_uuid);
        })
    })
}


const link_downloaders = document.querySelectorAll("a.link-downloader");
if (link_downloaders.length > 0) {
    let alert_header_content = `<i class="fa-solid fa-download fa-bounce"></i> Downloading`
    let alert_body_message = `Please wait, your download will begin shortly...`
    const alertElem = construct_alert_element("info", alert_header_content, alert_body_message)

    link_downloaders.forEach(link => {
        link.addEventListener("click", function(e) {
            add_alert(alertElem);

            var xhr = new XMLHttpRequest();
            xhr.open('GET', this.href, true);
            xhr.responseType = "blob";
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const contentDisposition = xhr.getResponseHeader('Content-Disposition');
                    const fileNameMatch = contentDisposition.match(/filename=([^;]+)/i);
                    const fileName = fileNameMatch ? fileNameMatch[1] : 'file';
                    const blob = xhr.response;
                    const d_link = document.createElement('a');
                    d_link.href = window.URL.createObjectURL(blob)
                    d_link.download = fileName;
                    d_link.click();

                    let alert_header_content = `<i class="fa-solid fa-square-check"></i> Success`
                    let alert_body_message = `Downloaded successfuly!`
                    const alertElem = construct_alert_element("success", alert_header_content, alert_body_message);
                    add_alert(alertElem);

                } else {

                    let alert_header_content = `<i class="fa-solid fa-circle-exclamation fa-bounce"></i> Error`;
                    let alert_body_text = `An error occured while downloading...`;
                    const alertElem = construct_alert_element("warning", alert_header_content, alert_body_text);

                    add_alert(alertElem);
                }
            };
            xhr.send();
            e.preventDefault();
        })
    })
}