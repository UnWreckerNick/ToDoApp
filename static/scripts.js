const apiUrl = "http://127.0.0.1:8000/todos/";
const loginUrl = "http://127.0.0.1:8000/users/login/";

let token = localStorage.getItem("access_token");

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch(loginUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        localStorage.setItem("access_token", token);
        showApp();
    } else {
        alert("Invalid credentials");
    }
});

document.getElementById("logout-button").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    token = null;
    showLogin();
});

async function loadTasks() {
    const response = await fetch(apiUrl, {
        headers: { Authorization: `Bearer ${token}` },
    });

    if (response.ok) {
        const tasks = await response.json();
        const tasksContainer = document.getElementById("tasks");
        tasksContainer.innerHTML = "";

        tasks.forEach((task) => {
            const taskDiv = document.createElement("div");
            taskDiv.className = "task";

            const taskTitle = document.createElement("h3");
            taskTitle.textContent = task.title;

            const taskDescription = document.createElement("p");
            taskDescription.textContent = task.description;

            taskDiv.appendChild(taskTitle);
            taskDiv.appendChild(taskDescription);
            tasksContainer.appendChild(taskDiv);
        });
    } else if (response.status === 401) {
        showLogin();
    }
}

document.getElementById("todo-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const deadline = document.getElementById("deadline").value;

    const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, description, deadline }),
    });

    if (response.ok) {
        loadTasks();
        e.target.reset();
    } else {
        alert("Error adding task");
    }
});

function showApp() {
    document.getElementById("auth-section").style.display = "none";
    document.getElementById("todo-form").style.display = "block";
    document.getElementById("logout-button").style.display = "block";
    loadTasks();
}

function showLogin() {
    document.getElementById("auth-section").style.display = "block";
    document.getElementById("todo-form").style.display = "none";
    document.getElementById("logout-button").style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
    if (token) {
        showApp();
    } else {
        showLogin();
    }
});