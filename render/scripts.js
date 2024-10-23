document.addEventListener('DOMContentLoaded', () => {
    const productImage = document.querySelector('#products img');
    productImage.addEventListener('click', () => {
        alert('You clicked on the Apple product!');
    });
});