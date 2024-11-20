let currentColumns = 3;
const MIN_COLUMNS = 2;
const MAX_COLUMNS = 4;

function updateColumns(change) {
    const newColumns = Math.min(Math.max(currentColumns + change, MIN_COLUMNS), MAX_COLUMNS);
    if (newColumns !== currentColumns) {
        currentColumns = newColumns;
        setColumns(currentColumns);
        updateColumnControls();
    }
}

function updateColumnControls() {
    document.getElementById('decreaseColumns').disabled = currentColumns <= MIN_COLUMNS;
    document.getElementById('increaseColumns').disabled = currentColumns >= MAX_COLUMNS;
    document.getElementById('columnCount').textContent = currentColumns;
}

function setColumns(cols) {
    // Update grid items width
    const items = document.querySelectorAll('.grid-item');
    const width = `${100/cols}%`;
    items.forEach(item => {
        item.style.width = width;
    });
    
    // Force Masonry to relayout
    const grid = document.querySelector('.grid');
    const masonry = Masonry.data(grid);
    if (masonry) {
        masonry.layout();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setColumns(currentColumns);
    updateColumnControls();
});
