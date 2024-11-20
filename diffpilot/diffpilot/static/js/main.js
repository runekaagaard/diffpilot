function setColumns(cols) {
    // Update active button state
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.btn-group .btn:nth-child(${cols-1})`).classList.add('active');
    
    // Update grid items width
    const items = document.querySelectorAll('.grid-item');
    const width = `${100/cols}%`;
    items.forEach(item => {
        item.style.width = width;
    });
    
    // Force Masonry to relayout
    const grid = document.querySelector('.grid');
    const masonry = Masonry.data(grid);
    masonry.layout();
}
