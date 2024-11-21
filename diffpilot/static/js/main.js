let currentColumns = 3;
const MIN_COLUMNS = 1;
const MAX_COLUMNS = 100;
let masonryInstance = null;

function initMasonry() {
    const grid = document.querySelector('.grid');
    masonryInstance = new Masonry(grid, {
        itemSelector: '.grid-item',
        percentPosition: true,
        columnWidth: '.grid-item',
        transitionDuration: '0.2s'
    });
}

function updateColumns(change) {
    const newColumns = Math.min(Math.max(currentColumns + change, MIN_COLUMNS), MAX_COLUMNS);
    if (newColumns !== currentColumns) {
        currentColumns = newColumns;
        setColumns(currentColumns);
        updateColumnControls();
        if (masonryInstance) {
            setTimeout(() => masonryInstance.layout(), 100);
        }
    }
}

function updateColumnControls() {
    const decreaseBtn = document.getElementById('decreaseColumns');
    const increaseBtn = document.getElementById('increaseColumns');
    const countDisplay = document.getElementById('columnCount');
    
    if (decreaseBtn) decreaseBtn.disabled = currentColumns <= MIN_COLUMNS;
    if (increaseBtn) increaseBtn.disabled = currentColumns >= MAX_COLUMNS;
    if (countDisplay) countDisplay.textContent = currentColumns;
}

function setColumns(cols) {
    // Update grid items width
    const items = document.querySelectorAll('.grid-item');
    const width = `${100/cols}%`;
    items.forEach(item => {
        item.style.width = width;
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initMasonry();
    setColumns(currentColumns);
    updateColumnControls();
});

// Re-layout after all images and content are loaded
window.addEventListener('load', function() {
    if (masonryInstance) {
        masonryInstance.layout();
    }
});
