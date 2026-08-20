
document.querySelectorAll(".tab").forEach((button)=>{
  button.addEventListener("click",()=>{
    document.querySelectorAll(".tab").forEach((b)=>b.classList.remove("active"));
    document.querySelectorAll(".result-panel").forEach((p)=>p.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(button.dataset.target).classList.add("active");
  });
});
const copyButton=document.getElementById("copyBib");
copyButton.addEventListener("click",async()=>{
  const text=document.getElementById("bibtex").innerText;
  try{
    await navigator.clipboard.writeText(text);
    copyButton.textContent="Copied";
    setTimeout(()=>copyButton.textContent="Copy",1500);
  }catch(e){copyButton.textContent="Select manually";}
});
