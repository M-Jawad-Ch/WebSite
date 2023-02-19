const input = document.getElementById('main-input');
const preview = document.getElementById('preview')

input.addEventListener('input', (event) => {
    preview.innerHTML = input.value;
})