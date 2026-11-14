document.addEventListener('DOMContentLoaded', () => {
    const incidentForm = document.getElementById('create-incident-form');
    if (incidentForm) {
        incidentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                title: incidentForm.title.value,
                description: incidentForm.description.value,
                priority: incidentForm.priority.value
            };

            const res = await fetch('/api/incidents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                window.location.reload();
            } else {
                alert('Failed to create incident');
            }
        });
    }

    const commentForm = document.getElementById('add-comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const incidentId = commentForm.dataset.incidentId;
            const data = {
                user_id: parseInt(commentForm.user_id.value),
                comment: commentForm.comment.value
            };

            const res = await fetch(`/api/incidents/${incidentId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                window.location.reload();
            } else {
                alert('Failed to add comment. Make sure the User ID exists in the system.');
            }
        });
    }

    const updateStatusForm = document.getElementById('update-status-form');
    if (updateStatusForm) {
        updateStatusForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const incidentId = updateStatusForm.getAttribute('data-incident-id');
            const newStatus = document.getElementById('status-select').value;

            try {
                const response = await fetch(`/api/incidents/${incidentId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ status: newStatus })
                });

                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('Failed to update incident status.');
                }
            } catch (error) {
                console.error('Error updating status:', error);
                alert('Network error while updating status.');
            }
        });
    }
});
