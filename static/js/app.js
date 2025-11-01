// public/static/js/app.js
document.getElementById("device-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    ip_address: document.getElementById("ip_address").value.trim(),
    username: document.getElementById("username").value.trim(),
    password: document.getElementById("password").value.trim(),
  };

  const res = await fetch("/api/devices", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (res.ok) {
    alert("บันทึกข้อมูลเรียบร้อยแล้ว!");
    e.target.reset();
  } else {
    const err = await res.json();
    alert("เกิดข้อผิดพลาด: " + (err.detail || res.statusText));
  }
});
