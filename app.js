const sideMenu = document.querySelector("aside");
const profileBtn = document.querySelector("#profile-btn");
const themeToggler = document.querySelector(".theme-toggler");

profileBtn.onclick = function() {
    sideMenu.classList.toggle('active');
}
window.onscroll = () => {
    sideMenu.classList.remove('active');
    if (window.scrollY > 0) { document.querySelector('header').classList.add('active'); }
    else { document.querySelector('header').classList.remove('active'); }
}

themeToggler.onclick = function() {
    document.body.classList.toggle('dark-theme');
    themeToggler.querySelector('span:nth-child(1)').classList.toggle('active')
    themeToggler.querySelector('span:nth-child(2)').classList.toggle('active')
}

// below function is done by vaishnavi
// function to check equality of passwords
function checkEquality(formName, input1 = "password", input2 = "repeatPassword", alertWhen = "no match") {
    var x = document.forms[formName][input1].value;
    var y = document.forms[formName][input2].value;
    if (x == y && alertWhen == "match") {
        alert('New password must be different from the old password');
        return false;
    }
    if (x != y && alertWhen == "no match") {
        alert('Password re-entered does not match');
        return false;
    }
    return true;
}