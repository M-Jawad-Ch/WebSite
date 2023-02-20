const title = document.getElementById('title-input')
const input = document.getElementById('main-input')
const preview = document.getElementById('preview')

input.addEventListener('input', (event) => {
    preview.innerHTML = input.value;
    title.style.color = 'black';
})

const postBtn = document.getElementById('post-btn')
postBtn.addEventListener('click', async (event) => {
    let res = await fetch(
        'http://localhost:5000/admin-post/publish',
        {
            method:'POST',
            body: JSON.stringify({
                'title':title.value,
                'body':input.value
            }),
            headers: {
                'Content-type':'application/json'
            }
        }
    )
    
    res = await res.json()

    if (res['status'] === 'failure') {
        title.style.color = 'red';
        preview.innerHTML = 'An existing post already has the title.'
    }
})