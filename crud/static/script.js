let aside = document.getElementById("aside");
let user = document.getElementById("user");
let aside_texts = document.querySelectorAll(".text");

setTimeout(() => {
  const messages = document.querySelectorAll('.message');
  messages.forEach(message => {
      message.style.opacity = '0';
      setTimeout(() => message.remove(), 500); // remove after transition
  });
}, 3000);


user.addEventListener("click", () => {
  aside.classList.toggle("active");
  aside.classList.value.indexOf("active") != -1
    ? aside_texts.forEach((e, i) =>
        setTimeout(() => e.classList.add("active"), 100 * (i + 1))
      )
    : aside_texts.forEach((e) => e.classList.remove("active"));
});

let add = document.getElementById("add").onclick = () => {
  console.log("xclick")
}

