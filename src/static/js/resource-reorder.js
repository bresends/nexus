document.addEventListener('DOMContentLoaded', function() {
    const resourcesList = document.getElementById('resourcesList');
    if (!resourcesList) return;

    let draggedItem = null;

    // Add event listeners for all draggable items
    document.querySelectorAll('.resource').forEach(row => {
        // Make only the drag handle initiate the drag
        const dragHandle = row.querySelector('.task__drag-handle');
        if (dragHandle) {
            dragHandle.addEventListener('mousedown', function() {
                row.setAttribute('draggable', true);
            });

            row.addEventListener('mouseup', function() {
                row.removeAttribute('draggable');
            });
        }

        row.addEventListener('dragstart', handleDragStart);
        row.addEventListener('dragend', handleDragEnd);
        row.addEventListener('dragover', handleDragOver);
        row.addEventListener('drop', handleDrop);
    });

    function handleDragStart(e) {
        draggedItem = this;
        this.classList.add('task--dragging');
    }

    function handleDragEnd(e) {
        this.classList.remove('task--dragging');
        draggedItem = null;
    }

    function handleDragOver(e) {
        e.preventDefault();
        const row = this;
        if (draggedItem && draggedItem !== row) {
            const draggingRect = draggedItem.getBoundingClientRect();
            const targetRect = row.getBoundingClientRect();
            const next = targetRect.top > draggingRect.top;
            if (next && row.nextSibling !== draggedItem) {
                row.parentNode.insertBefore(draggedItem, row.nextSibling);
            } else if (!next && row.previousSibling !== draggedItem) {
                row.parentNode.insertBefore(draggedItem, row);
            }
        }
    }

    function handleDrop(e) {
        e.preventDefault();
        if (!draggedItem) return;

        // Collect new order of resources
        const resourceOrders = Array.from(resourcesList.querySelectorAll('.resource')).map((row, index) => ({
            resourceId: parseInt(row.dataset.resourceId),
            order: index
        }));

        // Update resource numbers in the UI immediately
        updateResourceNumbers();

        // Get task ID from URL
        const taskId = getTaskId();
        if (!taskId) {
            console.error('Could not determine task ID from URL');
            return;
        }

        // Send order to server
        fetch(`/tasks/${taskId}/resources/reorder`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ resourceOrders })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                console.error('Error updating resource order:', data.message);
            }
        })
        .catch(error => {
            console.error('Error updating resource order:', error);
        });
    }

    // Helper function to get task ID from URL
    function getTaskId() {
        const path = window.location.pathname;
        const matches = path.match(/\/tasks\/(\d+)/);
        return matches ? matches[1] : null;
    }

    // Helper function to update resource numbers after reordering
    function updateResourceNumbers() {
        const rows = resourcesList.querySelectorAll('.resource');
        rows.forEach((row, index) => {
            const resourceNumberElement = row.querySelector('.task__number');
            if (resourceNumberElement) {
                resourceNumberElement.textContent = `${index + 1}`;
            }
        });
    }
});