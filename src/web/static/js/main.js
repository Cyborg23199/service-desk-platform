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
});
