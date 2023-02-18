let uname_inpt = document.getElementById('usr-name')
let psd_inpt = document.getElementById('psd')
let submit_btn = document.getElementById('submit')

uname_inpt.addEventListener('keypress', (event) => {
    if (event.key == 'Enter') event.preventDefault()
})

psd_inpt.addEventListener('keypress', (event) => {
    if (event.key == 'Enter') event.preventDefault()
})

submit_btn.addEventListener('click', async (event) => {
    event.preventDefault()

    let res = await fetch(
        'http://localhost:5000/verify', 
        {
            method:'POST',
            body:JSON.stringify({
                'username':uname_inpt.value,
                'password':psd_inpt.value
            }),
            headers:{
                'Content-type':'application/json',
            }})
    
    if (res.redirected) {
        window.location.href = res.url
    } else {
        alert('Incorrect Password or Username')
    }
})