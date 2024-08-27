document.querySelector('.hamburger').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var ariaExpanded = this.getAttribute('aria-expanded') === 'true';
    this.setAttribute('aria-expanded', !ariaExpanded);
    sidebar.classList.toggle('show');
    sidebar.setAttribute('aria-hidden', ariaExpanded);
});

document.querySelector('.close-btn').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var hamburger = document.querySelector('.hamburger');
    sidebar.classList.remove('show');
    sidebar.setAttribute('aria-hidden', 'true');
    hamburger.setAttribute('aria-expanded', 'false');
});

document.querySelector('#user-email').addEventListener('click', function() {
    var popup = document.querySelector('#email-popup');
    var isHidden = popup.getAttribute('aria-hidden') === 'true';
    popup.style.display = isHidden ? 'flex' : 'none';
    popup.setAttribute('aria-hidden', !isHidden);
});

document.addEventListener('click', function(event) {
    var popup = document.querySelector('#email-popup');
    var userInfo = document.querySelector('.user-info');
    if (!userInfo.contains(event.target)) {
        popup.style.display = 'none';
        popup.setAttribute('aria-hidden', 'true');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    let uploadedFiles = [];
    let deletedFiles = [];

    document.getElementById('images').addEventListener('change', function(event) {
        const fileList = event.target.files;
        const imagePreviewsContainer = document.getElementById('image-previews');
        // imagePreviewsContainer.innerHTML = ''; // Uncomment to clear previous previews

        for (let i = 0; i < fileList.length; i++) {
            uploadFile(fileList[i]);
        }

        event.target.value = ''; // Clear the input value to ensure re-uploading the same file works
    });

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        fetch("{% url 'upload_file' %}", {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const previewContainer = document.createElement('div');
                previewContainer.className = 'image-preview';

                const previewImage = document.createElement('img');
                previewImage.src = URL.createObjectURL(file);
                previewContainer.appendChild(previewImage);

                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-btn';
                deleteButton.textContent = 'Delete';
                deleteButton.addEventListener('click', function() {
                    const formData = new FormData();
                    formData.append('file_id', data.file_id);
                    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                    formData.append('delete_file', true);  // This flag helps identify the delete request in the view

                    fetch("{% url 'create_post' %}", {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            previewContainer.remove();
                            uploadedFiles = uploadedFiles.filter(id => id !== data.file_id);
                            updateUploadedFileIds();
                            updateFileCount();
                        } else {
                            console.error('Error:', data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });
                previewContainer.appendChild(deleteButton);

                document.getElementById('image-previews').appendChild(previewContainer);
                uploadedFiles.push(data.file_id);
                updateUploadedFileIds();
                updateFileCount();
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function deleteFile(previewContainer, fileId) {
        fetch("{% url 'delete_file' %}?file_id=" + fileId, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadedFiles = uploadedFiles.filter(id => id !== fileId);
                deletedFiles.push(fileId);
                previewContainer.remove();
                updateUploadedFileIds();
                updateDeletedFileIds();
                updateFileCount();
            } else {
                console.error('Error:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function updateUploadedFileIds() {
        document.getElementById('uploaded-file-ids').value = uploadedFiles.join(',');
    }

    function updateDeletedFileIds() {
        document.getElementById('deleted-file-ids').value = deletedFiles.join(',');
    }

    function updateFileCount() {
        const fileCount = document.getElementById('image-previews').children.length;
    }

    // Ensure files are included in final form submission
    document.querySelector('.create-post-form').addEventListener('submit', function(event) {
        updateUploadedFileIds();
        updateDeletedFileIds();
});

            
})
