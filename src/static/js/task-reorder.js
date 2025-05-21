document.addEventListener('DOMContentLoaded', function() {
    const tasksList = document.getElementById('tasksList');
    if (!tasksList) return;

    let draggedItem = null;

    // Add event listeners for all draggable items
    document.querySelectorAll('.task').forEach(row => {
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

        // Collect new order of tasks
        const taskOrders = Array.from(tasksList.querySelectorAll('.task')).map((row, index) => ({
            taskId: parseInt(row.dataset.taskId),
            order: index
        }));

        // Update task numbers in the UI immediately
        updateTaskNumbers();

        // Send order to server
        fetch(`/projects/${getProjectId()}/tasks/reorder`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ taskOrders })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                console.error('Error updating task order:', data.message);
            }
        })
        .catch(error => {
            console.error('Error updating task order:', error);
        });
    }

    // Helper function to get project ID from URL
    function getProjectId() {
        const path = window.location.pathname;
        const matches = path.match(/\/projects\/(\d+)/);
        return matches ? matches[1] : null;
    }

    // Helper function to update task numbers after reordering
    function updateTaskNumbers() {
        const rows = tasksList.querySelectorAll('.task');
        rows.forEach((row, index) => {
            const taskNumberElement = row.querySelector('.task__number');
            if (taskNumberElement) {
                taskNumberElement.textContent = `${index + 1}`;
            }
        });
    }
});
