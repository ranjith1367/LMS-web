if (window.location.pathname.includes("course-details.html")) {
    const courseId = getCourseIdFromUrl();

    (async function loadCourseDetails() {
        try {
            const [courseRes, categoriesRes] = await Promise.all([
                fetch("http://127.0.0.1:5000/api/courses/" + courseId),
                fetch("http://127.0.0.1:5000/api/categories")
            ]);

            const courseData = await courseRes.json();
            const categoriesData = await categoriesRes.json();

            if (!courseRes.ok) {
                document.getElementById("course-title").textContent = "Course not found";
                return;
            }

            const categoryMap = {};
            categoriesData.categories.forEach(function(cat) {
                categoryMap[cat.category_id] = cat.category_name;
            });

            const course = courseData.course;

            document.getElementById("course-title").textContent = course.title;
            document.getElementById("course-category").textContent = "Category: " + (categoryMap[course.category_id] || "Uncategorized");
            document.getElementById("course-rating").textContent = "Level: " + (course.level || "Not specified");
            document.getElementById("course-description").textContent = course.description || "No description available.";
        } catch (error) {
            console.log("Could not load course details:", error);
        }
    })();
}

function getCourseIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get("course_id") || params.get("course");

    if (!raw) return null;

    // Real numeric ID from the database: ?course=3 or ?course_id=3
    if (!isNaN(raw)) return Number(raw);

    // Old text links kept working: ?course=python
    const slugMap = { python: 1, webdesign: 8, datastructures: 6 };
    return slugMap[raw] || null;
}

const searchBox = document.getElementById("search-box");

if (searchBox) {
    searchBox.addEventListener("input", function() {
        const searchTerm = searchBox.value.toLowerCase();
        const cards = document.querySelectorAll(".course-card");

        cards.forEach(function(card) {
            const title = card.querySelector("h3").textContent.toLowerCase();

            if (title.includes(searchTerm)) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }
        });
    });
}

const courseForm = document.getElementById("create-course-form");

if (courseForm) {
    const token = localStorage.getItem("access_token");
    const categorySelect = document.getElementById("course-category");
    const formMessage = document.getElementById("form-message");

    // Load real categories into the dropdown
    (async function loadCategories() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/categories");
            const data = await response.json();

            if (response.ok) {
                data.categories.forEach(function(category) {
                    const option = document.createElement("option");
                    option.value = category.category_id;
                    option.textContent = category.category_name;
                    categorySelect.appendChild(option);
                });
            }
        } catch (error) {
            console.log("Could not load categories:", error);
        }
    })();

    courseForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const title = document.getElementById("course-title").value.trim();
        const categoryId = categorySelect.value;
        const thumbnail = document.getElementById("course-thumbnail").value.trim();
        const description = document.getElementById("course-description").value.trim();
        const objectives = document.getElementById("learning-objectives").value.trim();
        const level = document.getElementById("course-level").value;
        const duration = document.getElementById("course-duration").value;

        if (title === "" || categoryId === "" || description === "") {
            formMessage.textContent = "Please fill in Title, Category and Description.";
            formMessage.style.color = "#c0392b";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/courses", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    category_id: parseInt(categoryId),
                    title: title,
                    description: description,
                    learning_objectives: objectives || null,
                    thumbnail: thumbnail || null,
                    level: level || null,
                    duration: duration ? parseInt(duration) : null
                })
            });

            const data = await response.json();

            if (response.ok) {
                formMessage.textContent = "Course \"" + data.course.title + "\" created as Draft (course ID: " + data.course.course_id + ")!";
                formMessage.style.color = "#27ae60";
                courseForm.reset();
            } else {
                formMessage.textContent = data.message || "Could not create course.";
                formMessage.style.color = "#c0392b";
            }
        } catch (error) {
            formMessage.textContent = "Could not reach the server.";
            formMessage.style.color = "#c0392b";
        }
    });
}

const courseList = document.getElementById("course-list");

if (courseList) {
    (async function loadCourses() {
        try {
            const [coursesRes, categoriesRes] = await Promise.all([
                fetch("http://127.0.0.1:5000/api/courses"),
                fetch("http://127.0.0.1:5000/api/categories")
            ]);

            const coursesData = await coursesRes.json();
            const categoriesData = await categoriesRes.json();

            const categoryMap = {};
            categoriesData.categories.forEach(function(cat) {
                categoryMap[cat.category_id] = cat.category_name;
            });

            const publishedCourses = coursesData.courses.filter(function(course) {
                return course.status === "PUBLISHED";
            });

            courseList.innerHTML = "<div class='loading-state'><span class='spinner'></span>Loading courses...</div>";

            publishedCourses.forEach(function(course) {
                const card = document.createElement("div");
                card.className = "course-card";
                card.innerHTML =
                    "<h3>" + course.title + "</h3>" +
                    "<p>Course ID: " + course.course_id + "</p>" +
                    "<p>Category: " + (categoryMap[course.category_id] || "Uncategorized") + "</p>" +
                    "<p>Level: " + (course.level || "Not specified") + "</p>" +
                    "<a href='course-details.html?course=" + course.course_id + "'><button>View Details</button></a>";
                courseList.appendChild(card);
            });

            if (publishedCourses.length === 0) {
                courseList.innerHTML = "<div class='empty-state'><span class='empty-icon'>📚</span>No published courses available yet.</div>";
            }
        } catch (error) {
            courseList.innerHTML = "<p>Could not load courses.</p>";
        }
    })();
}

const myCoursesList = document.getElementById("my-courses-list");

if (myCoursesList) {
    const token = localStorage.getItem("access_token");

    function statusClass(status) {
        if (status === "PUBLISHED") return "status-published";
        if (status === "DRAFT" || status === "ARCHIVED") return "status-draft";
        return "status-pending"; // SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, REVISION, RESUBMITTED
    }

    async function loadMyCourses() {
    try {
        const response = await fetch("http://127.0.0.1:5000/api/courses/my", {
            headers: { "Authorization": "Bearer " + token }
        });
        const data = await response.json();

        myCoursesList.innerHTML = "";

        data.courses.forEach(function(course) {
            const item = document.createElement("div");
            item.className = "trainer-course-item";
            item.dataset.courseId = course.course_id;

            let workflowHTML = "";
            if (course.status === "DRAFT") {
                workflowHTML = "<button class='submit-course-btn'>Submit for Approval</button>";
            } else if (course.status === "REJECTED") {
                workflowHTML = "<button class='revise-course-btn'>Move to Revision</button>";
            } else if (course.status === "REVISION") {
                workflowHTML = "<button class='submit-course-btn'>Resubmit</button>";
            }

            item.innerHTML =
            "<div>" +
                "<h3>" + course.title + "</h3>" +
                "<p>Course ID: " + course.course_id + "</p>" +
                "<p>Status: <span class='status-badge " + statusClass(course.status) + "'>" + course.status + "</span></p>" +
            "</div>" +
            "<div class='trainer-course-actions'>" +
                "<button class='course-edit-btn'>Edit</button>" +
                "<button class='course-delete-btn'>Delete</button> " +
                "<a href='manage-course-content.html?course_id=" + course.course_id + "'><button type='button'>Manage Content</button></a> " +
                workflowHTML +
            "</div>";

            myCoursesList.appendChild(item);
            });

            attachCourseButtonEvents();
        } catch (error) {
            myCoursesList.innerHTML = "<p>Could not load your courses.</p>";
        }
    }

    function attachCourseButtonEvents() {
        document.querySelectorAll(".course-edit-btn").forEach(function(button) {
            button.addEventListener("click", async function() {
                const item = button.closest(".trainer-course-item");
                const courseId = item.dataset.courseId;
                const currentTitle = item.querySelector("h3").textContent;

                const newTitle = prompt("Course Title:", currentTitle);
                if (newTitle === null) return;

                const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + token
                    },
                    body: JSON.stringify({ title: newTitle })
                });

                const data = await response.json();
                if (response.ok) {
                    loadMyCourses();
                } else {
                    alert(data.message || "Could not update course.");
                }
            });
        });

        document.querySelectorAll(".course-delete-btn").forEach(function(button) {
            button.addEventListener("click", async function() {
                const item = button.closest(".trainer-course-item");
                const courseId = item.dataset.courseId;
                const courseName = item.querySelector("h3").textContent;

                if (!confirm("Delete \"" + courseName + "\"?")) return;

                const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId, {
                    method: "DELETE",
                    headers: { "Authorization": "Bearer " + token }
                });

                const data = await response.json();
                if (response.ok) {
                    loadMyCourses();
                } else {
                    alert(data.message || "Could not delete course.");
                }
            });
        });

        document.querySelectorAll(".submit-course-btn").forEach(function(button) {
            button.addEventListener("click", async function() {
                const courseId = button.closest(".trainer-course-item").dataset.courseId;
                const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/submit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                    if (response.ok) { loadMyCourses(); } else { alert(data.message || "Could not submit."); }
                });
            });

        document.querySelectorAll(".revise-course-btn").forEach(function(button) {
            button.addEventListener("click", async function() {
                const courseId = button.closest(".trainer-course-item").dataset.courseId;
                const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/revision", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                if (response.ok) { loadMyCourses(); } else { alert(data.message || "Could not move to revision."); }
            });
        });
    }

    loadMyCourses();
}

const approvalsList = document.getElementById("approvals-list");

if (approvalsList) {
    const token = localStorage.getItem("access_token");

    // Statuses that actually need admin attention on this page
    const relevantStatuses = ["SUBMITTED", "RESUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"];

    async function loadApprovals() {
        try {
            const [coursesRes, categoriesRes, usersRes] = await Promise.all([
                fetch("http://127.0.0.1:5000/api/courses"),
                fetch("http://127.0.0.1:5000/api/categories"),
                fetch("http://127.0.0.1:5000/api/users", { headers: { "Authorization": "Bearer " + token } })
            ]);

            const coursesData = await coursesRes.json();
            const categoriesData = await categoriesRes.json();
            const usersData = await usersRes.json();

            const categoryMap = {};
            categoriesData.categories.forEach(function(c) { categoryMap[c.category_id] = c.category_name; });

            const userMap = {};
            usersData.users.forEach(function(u) { userMap[u.user_id] = u.full_name; });

            const relevantCourses = coursesData.courses.filter(function(course) {
                return relevantStatuses.includes(course.status);
            });

            approvalsList.innerHTML = "";

            if (relevantCourses.length === 0) {
                approvalsList.innerHTML = "<p>No courses awaiting action right now.</p>";
                return;
            }

            relevantCourses.forEach(function(course) {
                const item = document.createElement("div");
                item.className = "approval-item";
                item.dataset.courseId = course.course_id;

                let actionsHTML = "";

                if (course.status === "SUBMITTED" || course.status === "RESUBMITTED") {
                    actionsHTML = "<button class='review-btn'>Start Review</button>";
                } else if (course.status === "UNDER_REVIEW") {
                    actionsHTML = "<button class='approve-btn'>Approve</button> <button class='reject-btn'>Reject</button>";
                } else if (course.status === "APPROVED") {
                    actionsHTML = "<button class='publish-btn'>Publish</button>";
                } else {
                    actionsHTML = "<span style='color:#5B6472;'>Awaiting trainer revision</span>";
                }

                item.innerHTML =
                    "<div>" +
                        "<h3>" + course.title + "</h3>" +
                        "<p>Submitted by: " + (userMap[course.trainer_id] || "Unknown") +
                        " | Category: " + (categoryMap[course.category_id] || "Uncategorized") +
                        " | Status: <span class='status-badge status-pending'>" + course.status + "</span></p>" +
                    "</div>" +
                    "<div class='approval-actions'>" + actionsHTML + "</div>";

                approvalsList.appendChild(item);
            });

            attachApprovalEvents();
        } catch (error) {
            approvalsList.innerHTML = "<p>Could not load courses.</p>";
        }
    }

    async function doWorkflowAction(courseId, action) {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/" + action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({})
            });

            const data = await response.json();

            if (response.ok) {
                loadApprovals();
            } else {
                alert(data.message || "Action failed.");
            }
        } catch (error) {
            alert("Could not reach the server.");
        }
    }

    function attachApprovalEvents() {
        document.querySelectorAll(".review-btn").forEach(function(btn) {
            btn.addEventListener("click", function() {
                doWorkflowAction(btn.closest(".approval-item").dataset.courseId, "review");
            });
        });
        document.querySelectorAll(".approve-btn").forEach(function(btn) {
            btn.addEventListener("click", function() {
                doWorkflowAction(btn.closest(".approval-item").dataset.courseId, "approve");
            });
        });
        document.querySelectorAll(".reject-btn").forEach(function(btn) {
            btn.addEventListener("click", function() {
                doWorkflowAction(btn.closest(".approval-item").dataset.courseId, "reject");
            });
        });
        document.querySelectorAll(".publish-btn").forEach(function(btn) {
            btn.addEventListener("click", function() {
                doWorkflowAction(btn.closest(".approval-item").dataset.courseId, "publish");
            });
        });
    }

    loadApprovals();
}

const assignmentSelect = document.getElementById("assignment-select");

if (assignmentSelect) {
    const token = localStorage.getItem("access_token");
    const courseId = 1; // Temporary: same hardcoded course used elsewhere
    const submissionsList = document.getElementById("submissions-list");

    (async function loadAssignmentOptions() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/assignments", {
                headers: { "Authorization": "Bearer " + token }
            });
            const data = await response.json();

            assignmentSelect.innerHTML = "<option value=''>-- Select --</option>";
            data.data.forEach(function(a) {
                const option = document.createElement("option");
                option.value = a.assignment_id;
                option.textContent = a.title;
                assignmentSelect.appendChild(option);
            });
        } catch (error) {
            assignmentSelect.innerHTML = "<option value=''>Could not load assignments</option>";
        }
    })();

    async function loadSubmissions(assignmentId) {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/assignments/" + assignmentId + "/submissions", {
                headers: { "Authorization": "Bearer " + token }
            });
            const data = await response.json();

            submissionsList.innerHTML = "";

            if (data.data.length === 0) {
                submissionsList.innerHTML = "<p>No submissions yet for this assignment.</p>";
                return;
            }

            data.data.forEach(function(sub) {
                const item = document.createElement("div");
                item.className = "evaluation-item";
                item.dataset.submissionId = sub.submission_id;

                const alreadyEvaluated = sub.status === "EVALUATED";

                item.innerHTML =
                    "<h3>Student ID: " + sub.student_id + " (Status: " + sub.status + ")</h3>" +
                    "<p>Comments: " + (sub.comments || "None") + "</p>" +
                    "<div class='form-group'>" +
                        "<label>Marks</label>" +
                        "<input type='number' class='eval-marks' min='0' value='" + (sub.marks !== null ? sub.marks : "") + "'>" +
                    "</div>" +
                    "<div class='form-group'>" +
                        "<label>Feedback</label>" +
                        "<textarea class='eval-feedback' rows='2'>" + (sub.feedback || "") + "</textarea>" +
                    "</div>" +
                    "<button class='eval-submit-btn'>" + (alreadyEvaluated ? "Update Evaluation" : "Submit Evaluation") + "</button>";

                submissionsList.appendChild(item);
            });

            attachEvalEvents();
        } catch (error) {
            submissionsList.innerHTML = "<p>Could not load submissions.</p>";
        }
    }

    function attachEvalEvents() {
        document.querySelectorAll(".eval-submit-btn").forEach(function(button) {
            button.addEventListener("click", async function() {
                const item = button.closest(".evaluation-item");
                const submissionId = item.dataset.submissionId;
                const marks = item.querySelector(".eval-marks").value;
                const feedback = item.querySelector(".eval-feedback").value.trim();

                if (marks === "") {
                    alert("Please enter marks.");
                    return;
                }

                try {
                    const response = await fetch("http://127.0.0.1:5000/api/submissions/" + submissionId + "/evaluate", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + token
                        },
                        body: JSON.stringify({
                            marks: parseFloat(marks),
                            feedback: feedback
                        })
                    });

                    const data = await response.json();

                    if (response.ok) {
                        alert("Evaluation saved!");
                        loadSubmissions(assignmentSelect.value);
                    } else {
                        alert(data.message || "Could not evaluate.");
                    }
                } catch (error) {
                    alert("Could not reach the server.");
                }
            });
        });
    }

    assignmentSelect.addEventListener("change", function() {
        if (assignmentSelect.value) {
            loadSubmissions(assignmentSelect.value);
        } else {
            submissionsList.innerHTML = "";
        }
    });
}

const API_BASE_URL = "http://127.0.0.1:5000";

const quizForm = document.getElementById("quiz-form");
const startQuizButton = document.getElementById("start-quiz-btn");

if (quizForm && startQuizButton) {
    const token = localStorage.getItem("access_token");

    const params = new URLSearchParams(window.location.search);
    const quizId = params.get("quiz_id") || params.get("quiz");

    const quizTitle = document.getElementById("quiz-title");
    const quizDescription = document.getElementById("quiz-description");
    const quizMessage = document.getElementById("quiz-message");
    const quizTimer = document.getElementById("quiz-timer");
    const questionsContainer =
        document.getElementById("questions-container");
    const submitQuizButton =
        document.getElementById("submit-quiz-btn");
    const quizResult =
        document.getElementById("quiz-result");

    let quizData = null;
    let attemptId = null;
    let timerInterval = null;
    let isSubmitting = false;

    function showMessage(message, color = "#c0392b") {
        quizMessage.textContent = message;
        quizMessage.style.color = color;
    }

    async function apiRequest(url, options = {}) {
        const requestOptions = {
            ...options,
            headers: {
                ...(options.body
                    ? { "Content-Type": "application/json" }
                    : {}),
                "Authorization": "Bearer " + token,
                ...(options.headers || {})
            }
        };

        const response = await fetch(
            API_BASE_URL + url,
            requestOptions
        );

        const data = await response.json().catch(function() {
            return {};
        });

        if (!response.ok) {
            throw new Error(
                data.message || "Request failed with status " + response.status
            );
        }

        return data;
    }

    function renderQuestions(questions) {
        questionsContainer.innerHTML = "";

        questions.forEach(function(question, index) {
            const questionBlock = document.createElement("div");
            questionBlock.className = "quiz-question";

            const heading = document.createElement("h3");
            heading.textContent =
                (index + 1) + ". " + question.question_text;

            questionBlock.appendChild(heading);

            const options = [
                ["A", question.option_a],
                ["B", question.option_b],
                ["C", question.option_c],
                ["D", question.option_d]
            ];

            options.forEach(function(option) {
                const label = document.createElement("label");
                label.style.display = "block";
                label.style.marginBottom = "8px";

                const input = document.createElement("input");
                input.type = "radio";
                input.name = "question-" + question.question_id;
                input.value = option[0];
                input.dataset.questionId = question.question_id;

                label.appendChild(input);
                label.appendChild(
                    document.createTextNode(
                        " " + option[0] + ". " + option[1]
                    )
                );

                questionBlock.appendChild(label);
            });

            questionsContainer.appendChild(questionBlock);
        });
    }

    function startTimer(minutes) {
        let remainingSeconds = Number(minutes) * 60;

        function updateTimer() {
            const displayMinutes =
                Math.floor(remainingSeconds / 60);

            const displaySeconds =
                remainingSeconds % 60;

            quizTimer.textContent =
                "Time left: " +
                displayMinutes +
                ":" +
                String(displaySeconds).padStart(2, "0");
        }

        updateTimer();

        timerInterval = setInterval(function() {
            remainingSeconds--;

            updateTimer();

            if (remainingSeconds <= 0) {
                clearInterval(timerInterval);
                showMessage(
                    "Time is over. Your quiz is being submitted.",
                    "#c0392b"
                );
                submitQuiz();
            }
        }, 1000);
    }

    function collectAnswers() {
        const answers = [];

        quizData.questions.forEach(function(question) {
            const selected = document.querySelector(
                "input[name='question-" +
                question.question_id +
                "']:checked"
            );

            if (selected) {
                answers.push({
                    question_id: Number(question.question_id),
                    selected_option: selected.value
                });
            }
        });

        return answers;
    }

    async function submitQuiz() {
        if (isSubmitting) {
            return;
        }

        isSubmitting = true;
        clearInterval(timerInterval);
        submitQuizButton.disabled = true;

        const answers = collectAnswers();

        try {
            const result = await apiRequest(
                "/api/quiz-attempts/" +
                attemptId +
                "/submit",
                {
                    method: "POST",
                    body: JSON.stringify({
                        answers: answers
                    })
                }
            );

            const score = result.data.score;
            const passed = result.data.passed;

            quizResult.textContent =
                "Your score: " +
                score +
                "%. " +
                (passed ? "Quiz Passed!" : "Quiz Failed.");

            quizResult.style.color =
                passed ? "#27ae60" : "#c0392b";

            showMessage(
                "Quiz submitted successfully.",
                "#27ae60"
            );
        } catch (error) {
            isSubmitting = false;
            submitQuizButton.disabled = false;

            showMessage(error.message);
        }
    }

    async function loadQuiz() {
        if (!token) {
            showMessage("Please log in before attempting the quiz.");
            startQuizButton.disabled = true;
            return;
        }

        if (!quizId) {
            showMessage(
                "Quiz ID is missing. Open the quiz from the course details page."
            );
            startQuizButton.disabled = true;
            return;
        }

        try {
            const result = await apiRequest(
                "/api/quizzes/" + quizId
            );

            quizData = result.data;

            quizTitle.textContent = quizData.title;
            quizDescription.textContent =
                quizData.description || "";

            renderQuestions(quizData.questions);

            showMessage(
                "Quiz loaded. Click Start Quiz.",
                "#27ae60"
            );
        } catch (error) {
            showMessage(error.message);
            startQuizButton.disabled = true;
        }
    }

    startQuizButton.addEventListener("click", async function() {
        startQuizButton.disabled = true;
        showMessage("Starting quiz...", "#5B6472");

        try {
            const result = await apiRequest(
                "/api/quizzes/" + quizId + "/attempts",
                {
                    method: "POST"
                }
            );

            attemptId = result.data.attempt_id;

            startQuizButton.hidden = true;
            quizForm.hidden = false;

            showMessage(
                "Quiz started. Good luck!",
                "#27ae60"
            );

            startTimer(quizData.time_limit);
        } catch (error) {
            startQuizButton.disabled = false;
            showMessage(error.message);
        }
    });

    quizForm.addEventListener("submit", function(event) {
        event.preventDefault();
        submitQuiz();
    });

    loadQuiz();
}

const assignmentForm = document.getElementById("assignment-form");

if (assignmentForm) {
    const token = localStorage.getItem("access_token");
    const params = new URLSearchParams(window.location.search);
    const assignmentId = params.get("assignment");
    const message = document.getElementById("submission-message");

    (async function loadAssignment() {
       if (!assignmentId) {
            message.textContent = "No assignment specified — open this page with a valid assignment link.";
            message.style.color = "#c0392b";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/assignments/" + assignmentId, {
                headers: { "Authorization": "Bearer " + token }
            });
            const data = await response.json();

            if (response.ok) {
                const a = data.data;
                document.getElementById("assignment-title").textContent = "Assignment: " + a.title;
                document.getElementById("assignment-description").textContent = a.description || "";
                document.getElementById("assignment-deadline").textContent = a.deadline;
                document.getElementById("assignment-max-marks").textContent = a.maximum_marks;
                document.getElementById("assignment-file-types").textContent = a.allowed_file_types || "Any";
            } else {
                document.getElementById("assignment-title").textContent = data.message || "Assignment not found.";
            }
        } catch (error) {
            document.getElementById("assignment-title").textContent = "Could not load assignment.";
        }
    })();

    assignmentForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const fileInput = document.getElementById("submission-file");
        const comments = document.getElementById("submission-comments").value.trim();

        if (fileInput.files.length === 0) {
            message.textContent = "Please choose a file before submitting.";
            message.style.color = "#c0392b";
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("comments", comments);

        try {
            const response = await fetch("http://127.0.0.1:5000/api/assignments/" + assignmentId + "/submit", {
                method: "POST",
                headers: {
                    "Authorization": "Bearer " + token
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                message.textContent = "Submitted successfully — awaiting evaluation.";
                message.style.color = "#27ae60";
                assignmentForm.reset();
            } else {
                message.textContent = data.message || "Could not submit assignment.";
                message.style.color = "#c0392b";
            }
        } catch (error) {
                message.textContent = "Could not reach the server.";
                message.style.color = "#c0392b";
            }
    });
}

const downloadBtn = document.getElementById("download-cert-btn");

if (downloadBtn) {
    downloadBtn.addEventListener("click", function() {
        window.print();
    });
}

const loginForm = document.getElementById("login-form");

if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();
        const loginMessage = document.getElementById("login-message");

        if (email === "" || password === "") {
            loginMessage.textContent = "Please fill in all fields.";
            loginMessage.style.color = "#c0392b";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("user_full_name", data.user.full_name);
                localStorage.setItem("user_role", data.user.role);

                loginMessage.textContent = "Login successful! Redirecting...";
                loginMessage.style.color = "#27ae60";

                const role = data.user.role;

                if (role === "Student") {
                    window.location.href = "dashboard.html";
                } else if (role === "Trainer") {
                    window.location.href = "trainer-dashboard.html";
                } else if (role === "Administrator") {
                    window.location.href = "admin-dashboard.html";
                }
            } else {
                loginMessage.textContent = data.message || "Login failed. Please try again.";
                loginMessage.style.color = "#c0392b";
            }
        } catch (error) {
            loginMessage.textContent = "Could not reach the server. Is the backend running?";
            loginMessage.style.color = "#c0392b";
        }
    });
}

const usersTableBody = document.getElementById("users-table-body");

if (usersTableBody) {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
    }

    function statusClass(status) {
        if (status === "ACTIVE") return "status-published";
        if (status === "SUSPENDED") return "status-pending";
        return "status-draft";
    }

    function renderUsers(users) {
        usersTableBody.innerHTML = "";

        users.forEach(function(user) {
            const row = document.createElement("tr");
            row.dataset.userId = user.user_id;

            const toggleLabel = user.status === "ACTIVE" ? "Suspend" : "Reactivate";
            const toggleClass = user.status === "ACTIVE" ? "user-suspend-btn" : "user-reactivate-btn";

            row.innerHTML =
            "<td>" + user.full_name + "</td>" +
            "<td>" + user.email + "</td>" +
            "<td>" + user.role + "</td>" +
            "<td><span class='status-badge " + statusClass(user.status) + "'>" + user.status + "</span></td>" +
            "<td>" +
                "<button class='user-edit-btn'>Edit</button> " +
                "<button class='" + toggleClass + "'>" + toggleLabel + "</button>" +
            "</td>";

            usersTableBody.appendChild(row);
        });
        attachUserButtonEvents();
    }

    async function loadUsers() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/users", {
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + token
                }
            });

            const data = await response.json();

            if (response.ok) {
                renderUsers(data.users);
            } else {
                usersTableBody.innerHTML = "<tr><td> colspan='5'>" + (data.message || "Could not load users.") + "</td></tr>";
            }
        } catch (error) {
            usersTableBody.innerHTML = "<tr><td colspan='5'>Could not reach the server.</td></tr>";
        }
    }

    async function updateUserStatus(userId, newStatus) {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/users/" + userId, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({ status: newStatus})
            });

            const data = await response.json();

            if (response.ok) {
                loadUsers();
            } else {
                alert(data.message || "Update failed.");
            }
        } catch (error) {
            alert("Could not reach the server.");
        }
    }

    function attachUserButtonEvents() {
        document.querySelectorAll(".user-edit-btn").forEach(function(button) {
            button.addEventListener("click", function() {
                const row = button.closest("tr");
                const userId = row.dataset.userId;
                const currentName = row.children[0].textContent;
                const currentEmail = row.children[1].textContent;

                const newName = prompt("FUll Name:", currentName);
                if (newName === null) return;

                const newEmail = prompt("Email:", currentEmail);
                if (newEmail === null) return;

                fetch("http://127.0.0.1:5000/api/users/" + userId, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + token
                    },
                    body: JSON.stringify({full_name: newName, email: newEmail })
                })
                .then(function(response) { return response.json(); })
                .then(function() { loadUsers(); });
            });
        });

        document.querySelectorAll(".user-suspend-btn").forEach(function(button) {
            button.addEventListener("click", function() {
                const userId = button.closest("tr").dataset.userId;
                updateUserStatus(userId, "SUSPENDED");
            });
        });

        document.querySelectorAll(".user-reactivate-btn").forEach(function(button) {
            button.addEventListener("click", function(){
                const userId = button.closest("tr").dataset.userId;
                updateUserStatus(userId, "ACTIVE");
            });
        });
    }
    loadUsers();
}

const verifyBtn = document.getElementById("verify-btn");

if (verifyBtn) {
        verifyBtn.addEventListener("click", async function() {
            const certNumber = document.getElementById("cert-input").value.trim();
            const result = document.getElementById("verify-result");
            
            if (certNumber === "") {
            result.innerHTML =
                "<p style='color: #c0392b; font-weight: bold;'>Please enter a certificate number.</p>";
            return;
            }

            result.innerHTML = "<p>Checking certificate...</p>";

            try {
            const response = await fetch("http://127.0.0.1:5000/api/certificates/verify/" + encodeURIComponent(certNumber));
            const data = await response.json();

            if (response.ok && data.valid) {
                const c = data.data;
                result.innerHTML =
                "<p style='color: #27ae60; font-weight: bold;'>&#10003; Valid Certificate</p>" +
                "<p>Student: " + (c.student_name || ("Student ID " + c.student_id)) + "</p>" +
                "<p>Course: " + (c.course_title || ("Course ID " + c.course_id)) + "</p>" +
                "<p>Issued on: " + (c.issued_at ? new Date(c.issued_at).toLocaleDateString() : "-") + "</p>";
                } else {
                result.innerHTML =
                "<p style='color: #c0392b; font-weight: bold;'>&#10007; Invalid Certificate Number</p>";
            } 
        } catch (error) {
                result.innerHTML = 
                "<p style='color: #c0392b; font-weight: bold;'>Could not reach the server. Is the backend running?</p>";
            }
        });
}

const reviewsList = document.getElementById("reviews-list");

if (reviewsList) {
    const token = localStorage.getItem("access_token");
    const courseId = new URLSearchParams(window.location.search).get("course");
    const ratingSummary = document.getElementById("rating-summary");
    const reviewForm = document.getElementById("review-form");
    const reviewMessage = document.getElementById("review-message");

    async function loadReviews() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/reviews");
            const data = await response.json();

            if (!response.ok) {
                reviewsList.innerHTML = "<p>Could not load reviews.</p>";
                return;
            }

            const { average_rating, review_count, reviews } = data.data;

            ratingSummary.textContent = review_count > 0
                ? "Average rating: " + average_rating + " / 5 (" + review_count + " review" + (review_count === 1 ? "" : "s") + ")"
                : "No ratings yet.";

            reviewsList.innerHTML = "";

            if (reviews.length === 0) {
                reviewsList.innerHTML = "<p>Be the first to review this course.</p>";
                return;
            }

            reviews.forEach(function(review) {
                const stars = "\u2605".repeat(review.rating) + "\u2606".repeat(5 - review.rating);
                const item = document.createElement("div");
                item.className = "review-item";
                item.innerHTML = "<p><strong>Student " + review.student_id + "</strong> — " + stars + "</p><p>" + (review.review_text || "") + "</p>";
                reviewsList.appendChild(item);
            });
        } catch (error) {
            reviewsList.innerHTML = "<p>Could not reach the server.</p>";
        }
    }

    reviewForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const rating = document.getElementById("review-rating").value;
        const text = document.getElementById("review-text").value.trim();

        if (rating === "" || text === "") {
            reviewMessage.textContent = "Please select a rating and write a review.";
            reviewMessage.style.color = "#c0392b";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/reviews", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    rating: parseInt(rating),
                    review_text: text
                })
            });

            const data = await response.json();

            if (response.ok) {
                reviewMessage.textContent = "Review submitted!";
                reviewMessage.style.color = "#27ae60";
                reviewForm.reset();
                loadReviews();
            } else {
                reviewMessage.textContent = data.message || "Could not submit review.";
                reviewMessage.style.color = "#c0392b";
            }
        } catch (error) {
            reviewMessage.textContent = "Could not reach the server.";
            reviewMessage.style.color = "#c0392b";
        }
    });

    loadReviews();
}

    const categoryList = document.getElementById("category-list");

    if (categoryList) {
        const token = localStorage.getItem("access_token");
        const categoryForm = document.getElementById("category-form");
        const categoryMessage = document.getElementById("category-message");

        function renderCategories(categories) {
            categoryList.innerHTML = "";

            categories.forEach(function(category) {
                const row = document.createElement("tr");
                row.dataset.categoryId = category.category_id;

                row.innerHTML = 
                "<td>" + category.category_name + "</td>" +
                "<td>" + (category.description || "-") + "</td>" +
                "<td>" +
                    "<button class='category-edit-btn'>Edit</button> " +
                    "<button class='category-delete-btn'>Delete</button> " +
                "</td>";

                categoryList.appendChild(row);
            });
            attachCategoryButtonEvents();
        }

        async function loadCategories() {
            try {
                const response = await fetch("http://127.0.0.1:5000/api/categories");
                const data = await response.json();

                if (response.ok) {
                    renderCategories(data.categories);
                } else {
                    categoryList.innerHTML = "<tr><td> colspan='3'>Could not load categories.</td></tr>";
                }
            } catch (error) {
                categoryList.innerHTML = "<tr><td colspan='3'>Could not reach the server.</td></tr>";
            }
        }

        function attachCategoryButtonEvents() {
            document.querySelectorAll(".category-edit-btn").forEach(function(button) {
                button.addEventListener("click", async function() {
                    const row = button.closest("tr");
                    const categoryId = row.dataset.categoryId;
                    const currentName = row.children[0].textContent;
                    const currentDescription = row.children[1].textContent;

                    const newName = prompt("Category Name:", currentName);
                    if (newName === null) return;

                    const newDescription = prompt("Description:", currentDescription === "-" ? "" : currentDescription);
                    if (newDescription === null) return;

                    try {
                        const response = await fetch("http://127.0.0.1:5000/api/categories/" + categoryId, {
                            method: "PUT",
                            headers: {
                                "Content-Type": "application/json",
                                "Authorization": "Bearer " + token
                            },
                            body: JSON.stringify({
                                category_name: newName,
                                description: newDescription
                            })
                        });

                        const data = await response.json();

                        if (response.ok) {
                            loadCategories();
                        } else {
                            alert(data.message || "Update failed.");
                        }
                    } catch (error) {
                        alert("Could not reach the server.");
                    }
                });
            });

            document.querySelectorAll(".category-delete-btn").forEach(function(button) {
                button.addEventListener("click", async function() {
                    const row = button.closest("tr");
                    const categoryId = row.dataset.categoryId;
                    const categoryName = row.children[0].textContent;

                    const confirmed = confirm("Delete category \"" + categoryName + "\"?");
                    if (!confirmed) return;

                    try {
                        const response = await fetch("http://127.0.0.1:5000/api/categories/" + categoryId, {
                            method: "DELETE",
                            headers: {
                                "Authorization": "Bearer " + token
                            }
                        });

                        const data = await response.json();

                        if (response.ok) {
                            loadCategories();
                        } else {
                            alert(data.message || "Delete failed.");
                        }
                    } catch (error) {
                        alert ("Could not reach the server.");
                    }
                });
            });
        }

        categoryForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const nameInput = document.getElementById("category-name");
            const descriptionInput = document.getElementById("category-description");
            const name = nameInput.value.trim();
            const description = descriptionInput.value.trim();

            if (name === "") return;

            try {
                const response = await fetch("http://127.0.0.1:5000/api/categories", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + token
                    },
                    body: JSON.stringify({
                        category_name: name,
                        description: description
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    nameInput.value = "";
                    descriptionInput.value = "";
                    categoryMessage.textContent = "";
                    loadCategories();
                } else {
                    categoryMessage.textContent = data.message || "Could not create category.";
                    categoryMessage.style.color = "#c0392b";
                }
            } catch (error) {
                categoryMessage.textContent = "Could not reach the server.";
                categoryMessage.style.color = "#c0392b";
            }
        });
        loadCategories();
    }

    const registerForm = document.getElementById("register-form");

    if (registerForm) {
        registerForm.addEventListener("submit", async function(event) {
            event.preventDefault();

            const fullName = document.getElementById("full-name").value.trim();
            const email = document.getElementById("reg-email").value.trim();
            const password = document.getElementById("reg-password").value;
            const confirmPassword = document.getElementById("confirm-password").value;
            const role = document.getElementById("reg-role").value;
            const registerMessage = document.getElementById("register-message");

            if (fullName === "" || email === "" || password === "" || role === "") {
                registerMessage.textContent = "Please fill in all required fields.";
                registerMessage.style.color = "#c0392b";
                return;
            }

            if (password !== confirmPassword) {
                registerMessage.textContent = "Passwords do not match.";
                registerMessage.style.color = "#c0392b";
                return;
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/api/auth/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        email: email,
                        password: password,
                        confirm_password: confirmPassword,
                        role: role.charAt(0).toUpperCase() + role.slice(1)
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    registerMessage.textContent = "Registration successful! You can now Log in.";
                    registerMessage.style.color = "#27ae60";
                    setTimeout(function () {
                        window.location.href = "index.html";
                    }, 2000);
                } else {
                    registerMessage.textContent = data.message || "Registration failed. Please try again.";
                    registerMessage.style.color = "#c0392b";
                }
            } catch (error) {
                registerMessage.textContent = "Could not reach the server. Is the backend running?";
                registerMessage.style.color = "#c0392b";
            }
        });
    }

const toggleButtons = document.querySelectorAll(".toggle-password");

toggleButtons.forEach(function(toggle) {
    toggle.addEventListener("click", function() {
        const targetId = toggle.dataset.target;
        const input = document.getElementById(targetId);

        if (input.type === "password") {
            input.type = "text";
            toggle.textContent = "Hide";
        } else {
            input.type = "password";
            toggle.textContent = "Show";
        }
    });
});

const profileForm = document.getElementById("profile-form");

if (profileForm) {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "index.html";
    } else {
        // Load the real profile data when the page opens
        (async function loadProfile() {
            try {
                const response = await fetch("http://127.0.0.1:5000/api/auth/profile", {
                    method: "GET",
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    document.getElementById("profile-id").value = data.user.user_id;
                    document.getElementById("profile-name").value = data.user.full_name;
                    document.getElementById("profile-email").value = data.user.email;
                    document.getElementById("profile-role").value = data.user.role;
                }
            } catch (error) {
                console.log("Could not load Profile: ", error);
            }
        })();
    }
    profileForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const fullName = document.getElementById("profile-name").value.trim();
        const email = document.getElementById("profile-email").value.trim();
        const profileMessage = document.getElementById("profile-message");

        try {
            const response = await fetch("http://127.0.0.1:5000/api/auth/profile", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email
                })
            });

            const data = await response.json();

            if (response.ok) {
                profileMessage.textContent = "Profile updated Successfully!";
                profileMessage.style.color = "#27ae60";
                localStorage.setItem("user_full_name", data.user.full_name);
            } else {
                profileMessage.textContent = data.message || "Update failed.";
                profileMessage.style.color = "#c0392b";
            }
        } catch (error) {
            profileMessage.textContent = "Could not reach the server.";
            profileMessage.style.color = "#c0392b";
        }
    });
}

const profilePicInput = document.getElementById("profile-pic-input");

if (profilePicInput) {
    profilePicInput.addEventListener("change", function() {
        const file = profilePicInput.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const preview = document.getElementById("profile-pic-preview");
                const placeholder = document.getElementById("profile-pic-placeholder");
                preview.src = event.target.result;
                preview.style.display = "block";
                placeholder.style.display = "none";
            };
            reader.readAsDataURL(file);
        }
    });
}

/* ================= TRAINER COURSE CONTENT ================= */

const trainerModuleList =
    document.getElementById("module-list");

const trainerAddModuleForm =
    document.getElementById("add-module-form");

if (trainerModuleList && trainerAddModuleForm) {
    const token = localStorage.getItem("access_token");

    const params =
        new URLSearchParams(window.location.search);

    const courseId = params.get("course_id");

    const messageElement =
        document.getElementById("trainer-content-message");

    function showTrainerMessage(message, color) {
        messageElement.textContent = message;
        messageElement.style.color = color;
    }

    async function trainerApiRequest(
        path,
        options = {}
    ) {
        const response = await fetch(
            API_BASE_URL + path,
            {
                ...options,
                headers: {
                    "Authorization":
                        "Bearer " + token,
                    ...(options.body &&
                    !(options.body instanceof FormData)
                        ? {
                            "Content-Type":
                                "application/json"
                        }
                        : {}),
                    ...(options.headers || {})
                }
            }
        );

        const data = await response.json().catch(
            function () {
                return {};
            }
        );

        if (!response.ok) {
            throw new Error(
                data.message ||
                "Request failed with status " +
                response.status
            );
        }

        return data;
    }

    async function loadTrainerModules() {
        const courseId = params.get("course_id");
        const messageElement = document.getElementById("trainer-content-message");
        if (!courseId) {
            document.getElementById("manage-course-title").textContent = "No course selected";
             messageElement.textContent = "Please open this page from a specific course in your 'My Courses' list.";
            trainerModuleList.innerHTML = "";
            } else {
        }

        try {
            const result =
                await trainerApiRequest(
                    "/api/courses/" +
                    courseId +
                    "/modules"
                );

            const modules =
                result.modules || [];

            if (!modules.length) {
                trainerModuleList.innerHTML =
                    "<p>No modules created yet.</p>";
                return;
            }

            trainerModuleList.innerHTML = "";

            for (const module of modules) {
                const moduleBlock =
                    document.createElement("article");

                moduleBlock.className =
                    "module-block";

                moduleBlock.dataset.moduleId =
                    module.module_id;

                moduleBlock.innerHTML = `
                    <div class="module-header">
                        <h3>
                            Module ${module.module_order}:
                            ${module.module_name}
                        </h3>

                        <button
                            type="button"
                            class="delete-module-btn">
                            Delete Module
                        </button>
                    </div>

                    <p>
                        ${module.description || ""}
                    </p>

                    <div class="trainer-lesson-list">
                        <p>Loading lessons...</p>
                    </div>

                    <form
                        class="add-lesson-form"
                        data-module-id="${module.module_id}">

                        <h4>Add Lesson</h4>

                        <input
                            type="text"
                            name="lesson_name"
                            required
                            placeholder="Lesson name">

                        <textarea
                            name="description"
                            placeholder="Lesson description">
                        </textarea>

                        <input
                            type="number"
                            name="lesson_order"
                            min="1"
                            required
                            placeholder="Lesson order">

                        <button type="submit">
                            Add Lesson
                        </button>
                    </form>
                `;

                trainerModuleList.appendChild(
                    moduleBlock
                );

                await loadTrainerLessons(
                    moduleBlock,
                    module.module_id
                );
            }
        } catch (error) {
            trainerModuleList.innerHTML =
                "<p>Unable to load modules: " +
                error.message +
                "</p>";
        }
    }

    async function loadTrainerLessons(
        moduleBlock,
        moduleId
    ) {
        const lessonList =
            moduleBlock.querySelector(
                ".trainer-lesson-list"
            );

        try {
            const result =
                await trainerApiRequest(
                    "/api/modules/" +
                    moduleId +
                    "/lessons"
                );

            const lessons =
                result.lessons || [];

            if (!lessons.length) {
                lessonList.innerHTML =
                    "<p>No lessons created yet.</p>";
                return;
            }

            lessonList.innerHTML = "";

            lessons.forEach(function (lesson) {
                const lessonElement =
                    document.createElement("div");

                lessonElement.className =
                    "trainer-lesson";

                lessonElement.dataset.lessonId =
                    lesson.lesson_id;

                lessonElement.innerHTML = `
                    <p>
                        Lesson ${lesson.lesson_order}:
                        ${lesson.lesson_name}
                    </p>

                    <button
                        type="button"
                        class="delete-lesson-btn">
                        Delete Lesson
                    </button>

                    <form
                        class="upload-material-form"
                        data-lesson-id="${lesson.lesson_id}">

                        <input
                            type="text"
                            name="material_name"
                            required
                            placeholder="Material name">

                        <input
                            type="file"
                            name="file"
                            accept=".pdf,.mp4"
                            required>

                        <button type="submit">
                            Upload Material
                        </button>
                    </form>
                `;

                lessonList.appendChild(
                    lessonElement
                );
            });
        } catch (error) {
            lessonList.innerHTML =
                "<p>Unable to load lessons.</p>";
        }
    }

    trainerAddModuleForm.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            const moduleName =
                document.getElementById(
                    "module-name"
                ).value.trim();

            const description =
                document.getElementById(
                    "module-description"
                ).value.trim();

            const moduleOrder =
                document.getElementById(
                    "module-order"
                ).value;

            try {
                await trainerApiRequest(
                    "/api/courses/" +
                    courseId +
                    "/modules",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            module_name: moduleName,
                            description: description,
                            module_order:
                                Number(moduleOrder)
                        })
                    }
                );

                trainerAddModuleForm.reset();

                showTrainerMessage(
                    "Module created successfully.",
                    "#27ae60"
                );

                await loadTrainerModules();
            } catch (error) {
                showTrainerMessage(
                    error.message,
                    "#c0392b"
                );
            }
        }
    );

    trainerModuleList.addEventListener(
        "submit",
        async function (event) {
            const form =
                event.target.closest(
                    ".add-lesson-form"
                );

            if (!form) {
                return;
            }

            event.preventDefault();

            const moduleId =
                form.dataset.moduleId;

            const lessonName =
                form.elements.lesson_name.value.trim();

            const description =
                form.elements.description.value.trim();

            const lessonOrder =
                form.elements.lesson_order.value;

            try {
                await trainerApiRequest(
                    "/api/modules/" +
                    moduleId +
                    "/lessons",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            lesson_name: lessonName,
                            description: description,
                            lesson_order:
                                Number(lessonOrder)
                        })
                    }
                );

                showTrainerMessage(
                    "Lesson created successfully.",
                    "#27ae60"
                );

                await loadTrainerModules();
            } catch (error) {
                showTrainerMessage(
                    error.message,
                    "#c0392b"
                );
            }
        }
    );

    trainerModuleList.addEventListener(
        "submit",
        async function (event) {
            const form =
                event.target.closest(
                    ".upload-material-form"
                );

            if (!form) {
                return;
            }

            event.preventDefault();

            const lessonId =
                form.dataset.lessonId;

            const formData =
                new FormData(form);

            try {
                await trainerApiRequest(
                    "/api/lessons/" +
                    lessonId +
                    "/materials",
                    {
                        method: "POST",
                        body: formData
                    }
                );

                showTrainerMessage(
                    "Material uploaded successfully.",
                    "#27ae60"
                );

                form.reset();
            } catch (error) {
                showTrainerMessage(
                    error.message,
                    "#c0392b"
                );
            }
        }
    );

    trainerModuleList.addEventListener(
        "click",
        async function (event) {
            const deleteModuleButton =
                event.target.closest(
                    ".delete-module-btn"
                );

            if (deleteModuleButton) {
                const moduleBlock =
                    deleteModuleButton.closest(
                        ".module-block"
                    );

                const moduleId =
                    moduleBlock.dataset.moduleId;

                const confirmed = confirm(
                    "Delete this module and its lessons?"
                );

                if (!confirmed) {
                    return;
                }

                try {
                    await trainerApiRequest(
                        "/api/modules/" +
                        moduleId,
                        {
                            method: "DELETE"
                        }
                    );

                    await loadTrainerModules();
                } catch (error) {
                    showTrainerMessage(
                        error.message,
                        "#c0392b"
                    );
                }

                return;
            }

            const deleteLessonButton =
                event.target.closest(
                    ".delete-lesson-btn"
                );

            if (deleteLessonButton) {
                const lessonElement =
                    deleteLessonButton.closest(
                        ".trainer-lesson"
                    );

                const lessonId =
                    lessonElement.dataset.lessonId;

                const confirmed = confirm(
                    "Delete this lesson?"
                );

                if (!confirmed) {
                    return;
                }

                try {
                    await trainerApiRequest(
                        "/api/lessons/" +
                        lessonId,
                        {
                            method: "DELETE"
                        }
                    );

                    await loadTrainerModules();
                } catch (error) {
                    showTrainerMessage(
                        error.message,
                        "#c0392b"
                    );
                }
            }
        }
    );

    loadTrainerModules();
    
}

const addQuestionBtn = document.getElementById("add-question-btn");

if (addQuestionBtn) {
    const token = localStorage.getItem("access_token");
    const courseId = 1; // Temporary: same hardcoded course as assignments

    const questionList = document.getElementById("question-list");

    function attachRemoveQuestionEvent(button) {
        button.addEventListener("click", function() {
            const totalQuestions = document.querySelectorAll(".question-block").length;
            if (totalQuestions <= 1) {
                alert("A quiz must have at least one question.");
                return;
            }
            button.closest(".question-block").remove();
        });
    }

    document.querySelectorAll(".remove-question-btn").forEach(attachRemoveQuestionEvent);

    addQuestionBtn.addEventListener("click", function() {
        const newQuestion = document.createElement("div");
        newQuestion.className = "question-block";
        newQuestion.innerHTML =
            "<div class='form-group'>" +
                "<label>Question Text</label>" +
                "<input type='text' class='question-text' placeholder='Enter the question'>" +
            "</div>" +
            "<div class='options-grid'>" +
                "<input type='text' class='option-input' placeholder='Option A'>" +
                "<input type='text' class='option-input' placeholder='Option B'>" +
                "<input type='text' class='option-input' placeholder='Option C'>" +
                "<input type='text' class='option-input' placeholder='Option D'>" +
            "</div>" +
            "<div class='quiz-settings-row'>" +
                "<div class='form-group'>" +
                    "<label>Correct Option</label>" +
                    "<select class='correct-option'>" +
                        "<option value='A'>A</option>" +
                        "<option value='B'>B</option>" +
                        "<option value='C'>C</option>" +
                        "<option value='D'>D</option>" +
                    "</select>" +
                "</div>" +
                "<div class='form-group'>" +
                    "<label>Marks</label>" +
                    "<input type='number' class='question-marks' value='5' min='1'>" +
                "</div>" +
            "</div>" +
            "<button class='remove-question-btn'>Remove Question</button>";

        questionList.appendChild(newQuestion);
        attachRemoveQuestionEvent(newQuestion.querySelector(".remove-question-btn"));
    });

    const saveQuizBtn = document.getElementById("save-quiz-btn");
    const quizMessage = document.getElementById("quiz-save-message");

    saveQuizBtn.addEventListener("click", async function() {
        const quizTitle = document.getElementById("quiz-title").value.trim();
        const moduleId = document.getElementById("quiz-module").value;
        const timeLimit = document.getElementById("quiz-time-limit").value;
        const maxAttempts = document.getElementById("quiz-max-attempts").value;
        const passingScore = document.getElementById("quiz-passing-score").value;

        if (quizTitle === "") {
            quizMessage.textContent = "Please enter a quiz title.";
            quizMessage.style.color = "#c0392b";
            return;
        }

        const questionBlocks = document.querySelectorAll(".question-block");
        let allQuestionsFilled = true;

        questionBlocks.forEach(function(block) {
            const questionText = block.querySelector(".question-text").value.trim();
            const options = block.querySelectorAll(".option-input");
            let optionsFilled = true;

            options.forEach(function(option) {
                if (option.value.trim() === "") optionsFilled = false;
            });

            if (questionText === "" || !optionsFilled) {
                allQuestionsFilled = false;
            }
        });

        if (!allQuestionsFilled) {
            quizMessage.textContent = "Please fill in all questions and their 4 options before saving.";
            quizMessage.style.color = "#c0392b";
            return;
        }

        quizMessage.textContent = "Saving quiz...";
        quizMessage.style.color = "#5B6472";

        try {
            // Step 1: create the quiz itself
            const quizResponse = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/quizzes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    module_id: moduleId === "" ? null : parseInt(moduleId),
                    title: quizTitle,
                    time_limit: parseInt(timeLimit),
                    maximum_attempts: parseInt(maxAttempts),
                    passing_score: parseFloat(passingScore)
                })
            });

            const quizData = await quizResponse.json();

            if (!quizResponse.ok) {
                quizMessage.textContent = quizData.message || "Could not create quiz.";
                quizMessage.style.color = "#c0392b";
                return;
            }

            const newQuizId = quizData.data.quiz_id;

            // Step 2: create each question, one request per question
            for (const block of questionBlocks) {
                const options = block.querySelectorAll(".option-input");

                const questionResponse = await fetch("http://127.0.0.1:5000/api/quizzes/" + newQuizId + "/questions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + token
                    },
                    body: JSON.stringify({
                        question_text: block.querySelector(".question-text").value.trim(),
                        option_a: options[0].value.trim(),
                        option_b: options[1].value.trim(),
                        option_c: options[2].value.trim(),
                        option_d: options[3].value.trim(),
                        correct_option: block.querySelector(".correct-option").value,
                        marks: parseFloat(block.querySelector(".question-marks").value)
                    })
                });

                if (!questionResponse.ok) {
                    const questionData = await questionResponse.json();
                    quizMessage.textContent = "Quiz created, but a question failed: " + (questionData.message || "unknown error");
                    quizMessage.style.color = "#c0392b";
                    return;
                }
            }

            quizMessage.textContent = "Quiz saved successfully with " + questionBlocks.length + " question(s)!";
            quizMessage.style.color = "#27ae60";
        } catch (error) {
            quizMessage.textContent = "Could not reach the server.";
            quizMessage.style.color = "#c0392b";
        }
    });
}

if (window.location.pathname.includes("course-details.html")) {
    const token = localStorage.getItem("access_token");

    const backendCourseId = getCourseIdFromUrl();
    const takeQuizLink = document.getElementById("take-quiz-link");
    const quizLinkMessage =
        document.getElementById("quiz-link-message");

    async function loadCourseQuizLink() {
        if (!takeQuizLink || !quizLinkMessage) {
            return;
        }

        if (!token) {
            takeQuizLink.style.display = "none";
            quizLinkMessage.textContent =
                "Please log in to view quizzes.";
            return;
        }

        if (!backendCourseId) {
            takeQuizLink.style.display = "none";
            quizLinkMessage.textContent =
                "Course ID was not found.";
            return;
        }

        try {
            const response = await fetch(
                API_BASE_URL +
                "/api/courses/" +
                backendCourseId +
                "/quizzes",
                {
                    method: "GET",
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                }
            );

            const result = await response.json();

            if (!response.ok) {
                takeQuizLink.style.display = "none";
                quizLinkMessage.textContent =
                    result.message || "Could not load quizzes.";
                return;
            }

            const quizzes = result.data || [];

            if (quizzes.length === 0) {
                takeQuizLink.style.display = "none";
                quizLinkMessage.textContent =
                    "No quiz is available for this course.";
                return;
            }

            const firstQuizId = quizzes[0].quiz_id;

            takeQuizLink.href =
                "quiz.html?quiz_id=" + firstQuizId;

            quizLinkMessage.textContent =
                quizzes[0].title || "Quiz available";
            quizLinkMessage.style.color = "#27ae60";
        } catch (error) {
            takeQuizLink.style.display = "none";
            quizLinkMessage.textContent =
                "Could not load the course quiz.";
        }
    }

    loadCourseQuizLink();
}

const createAssignmentForm = document.getElementById("create-assignment-form");

if (createAssignmentForm) {
    const token = localStorage.getItem("access_token");
    const courseId = 1; // Temporary: hardcoded until a real course-selection page exists

    createAssignmentForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const title = document.getElementById("assignment-title").value.trim();
        const moduleId = document.getElementById("assignment-module").value;
        const description = document.getElementById("assignment-description").value.trim();
        const maxMarks = document.getElementById("assignment-max-marks").value;
        const rawDeadline = document.getElementById("assignment-deadline").value;
        const fileTypes = document.getElementById("assignment-file-types").value.trim();
        const message = document.getElementById("assignment-create-message");

        if (title === "" || moduleId === "" || description === "" || rawDeadline === "") {
            message.textContent = "Please fill in all required fields.";
            message.style.color = "#c0392b";
            return;
        }

        const deadlineDate = new Date(rawDeadline);
        if(deadlineDate <= new Date()) {
            message.textContent = "Deadline must be a future date and time.";
            message.style.color = "#c0392b";
            return;
        }

        try {
            const response = await fetch ("http://127.0.0.1:5000/api/courses/" + courseId + "/assignments", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({
                    module_id: parseInt(moduleId),
                    title: title,
                    description: description,
                    maximum_marks: parseFloat(maxMarks),
                    deadline: rawDeadline.replace("T", " ") + ":00",
                    allowed_file_types: fileTypes
                })
            });

            const data = await response.json();

            if (response.ok) {
                message.textContent = "Assignment \"" + data.data.title + "\" created successfully!";
                message.style.color = "#27ae60";
                createAssignmentForm.reset();
            } else {
                message.textContent = data.message || "Could not create assignment.";
                message.style.color = "#c0392b";
            }
        } catch (error) {
            message.textContent = "Could not reach the server.";
            message.style.color = "#c0392b";
        }
    });
}

const forgetPasswordForm = document.getElementById("forget-password-form");

if (forgetPasswordForm) {
    forgetPasswordForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const email = document.getElementById("forget-email").value.trim();
        const message = document.getElementById("forget-password-message");

        if (email === "") {
            message.textContent = "Please Enter Your Email";
            message.style.color = "#c0392b";
            return;
        }

        message.textContent = "If that email is registered, a reset link has been sent.";
        message.style.color = "#27ae60";
    });
}


// ================= DASHBOARD WELCOME =================

const welcomeUser = document.getElementById("welcome-user");

if (welcomeUser) {
    const fullName = localStorage.getItem("user_full_name");

    if (fullName) {
        welcomeUser.textContent = "Welcome, " + fullName;
    }
}




// ================= MY CERTIFICATES =================

const certificatesContainer = document.getElementById("certificates-container");

if (certificatesContainer) {

    const token = localStorage.getItem("access_token");

    const params = new URLSearchParams(window.location.search);
    const selectedCourseId = params.get("course_id");

    if (!token) {

        certificatesContainer.innerHTML =
            "<p>You haven't earned a certificate for this course yet — this requires 90%+ progress, all assignments graded, and a passing final assessment score.</p>";

    } else {

        fetch("http://127.0.0.1:5000/api/certificates", {
            headers: {
                "Authorization": "Bearer " + token
            }
        })
        .then(response => {

            if (!response.ok) {
                throw new Error("Certificate API failed");
            }

            return response.json();
        })
        .then(data => {

            if (!data.success || !data.data) {

                certificatesContainer.innerHTML =
                    "<p>No certificates available.</p>";

                return;
            }

            let certificates = data.data;

            // Show only the selected course certificate
            if (selectedCourseId) {

                certificates = certificates.filter(
                    certificate =>
                        String(certificate.course_id) === String(selectedCourseId)
                );
            }

            if (certificates.length === 0) {

                certificatesContainer.innerHTML =
                    "<p>No certificate available for this course.</p>";

                return;
            }

            certificatesContainer.innerHTML = "";

            certificates.forEach(certificate => {

                const certificateDiv = document.createElement("div");

                certificateDiv.className = "certificate";

                certificateDiv.innerHTML = `
                    <h2>Certificate of Completion</h2>

                    <p>This is to certify that</p>

                    <h2>${certificate.student_name}</h2>

                    <p>has successfully completed the course</p>

                    <h3>${certificate.course_title}</h3>

                    <p>
                        Certificate No:
                        ${certificate.certificate_number}
                    </p>

                    <p>
                        Issued on:
                        ${new Date(certificate.issued_at).toLocaleDateString()}
                    </p>

                    <br>

                    <button
                        class="download-certificate-btn"
                        data-certificate-id="${certificate.certificate_id}">
                        Download Certificate
                    </button>
                `;

                certificatesContainer.appendChild(certificateDiv);
            });

        })
        .catch(error => {

            console.error("Certificate error:", error);

            certificatesContainer.innerHTML =
                "<p>Unable to load certificates.</p>";
        });
    }
}


// ================= DOWNLOAD CERTIFICATE =================

document.addEventListener("click", function(event) {

    if (!event.target.classList.contains("download-certificate-btn")) {
        return;
    }

    const certificateId =
        event.target.getAttribute("data-certificate-id");

    const token =
        localStorage.getItem("access_token");

    if (!token) {
        alert("Please login first.");
        return;
    }

    fetch(
        "http://127.0.0.1:5000/api/certificates/" +
        certificateId +
        "/download",
        {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        }
    )
    .then(response => {

        if (!response.ok) {
            throw new Error("Certificate download failed");
        }

        return response.blob();
    })
    .then(blob => {

        const url = window.URL.createObjectURL(blob);

        const link = document.createElement("a");

        link.href = url;
        link.download = "certificate.pdf";

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(url);
    })
    .catch(error => {

        console.error("Download error:", error);

        alert("Unable to download certificate.");
    });

});


/* ================= MY ENROLLMENTS ================= */

const enrollmentsBody = document.getElementById("enrollments-body");

if (enrollmentsBody) {

    const token = localStorage.getItem("access_token");

    if (!token) {

        enrollmentsBody.innerHTML = `
            <tr>
                <td colspan="4">Please login first.</td>
            </tr>
        `;

    } else {

        fetch("http://127.0.0.1:5000/api/enrollments/my", {
            headers: {
                "Authorization": "Bearer " + token
            }
        })
        .then(response => {

            if (!response.ok) {
                throw new Error("Failed to load enrollments");
            }

            return response.json();
        })
        .then(data => {

            if (!data.success || !data.courses || data.courses.length === 0) {

                enrollmentsBody.innerHTML = `
                    <tr>
                        <td colspan="4">No enrollments found.</td>
                    </tr>
                `;

                return;
            }

            enrollmentsBody.innerHTML = "";

            data.courses.forEach(course => {

                const row = document.createElement("tr");

                const enrolledDate = course.enrolled_at
                    ? new Date(course.enrolled_at).toLocaleDateString("en-GB", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    })
                    : "-";

                let action = "--";

                if (course.status === "COMPLETED") {

                    action = `
                        <a href="certificate.html?course_id=${course.course_id}">
                            View Certificate
                        </a>
                    `;

                } else if (course.status === "ACTIVE") {

                    action = `
                        <a href="course-details.html?course_id=${course.course_id}">
                            Continue Learning
                        </a>
                    `;
                }

                row.innerHTML = `
                    <td>${course.course_title}</td>
                    <td>${enrolledDate}</td>
                    <td>
                        <span class="status-badge">
                            ${course.status}
                        </span>
                    </td>
                    <td>${action}</td>
                `;

                enrollmentsBody.appendChild(row);
            });

        })
        .catch(error => {

            console.error("Enrollment error:", error);

            enrollmentsBody.innerHTML = `
                <tr>
                    <td colspan="4">
                        Unable to load enrollments.
                    </td>
                </tr>
            `;
        });
    }
}

/* ================= ENROLL IN COURSE ================= */

const enrollBtn = document.getElementById("enroll-btn");
const enrollMessage = document.getElementById("enroll-message");

if (enrollBtn) {
    const token = localStorage.getItem("access_token");
    const courseIdForEnroll = getCourseIdFromUrl();

    enrollBtn.addEventListener("click", async function() {
        if (!token) {
            enrollMessage.textContent = "Please log in to enroll.";
            enrollMessage.style.color = "#c0392b";
            return;
        }

        if (!courseIdForEnroll) {
            enrollMessage.textContent = "Course ID was not found.";
            enrollMessage.style.color = "#c0392b";
            return;
        }

        enrollBtn.disabled = true;
        enrollMessage.textContent = "Enrolling...";
        enrollMessage.style.color = "#5B6472";

        try {
            const response = await fetch(
                "http://127.0.0.1:5000/api/courses/" + courseIdForEnroll + "/enroll",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + token
                    },
                    body: JSON.stringify({})
                }
            );

            const data = await response.json();

            if (response.ok) {
                enrollMessage.textContent = "Enrolled successfully!";
                enrollMessage.style.color = "#27ae60";
                enrollBtn.textContent = "Enrolled";
            } else {
                enrollMessage.textContent = data.message || "Could not enroll.";
                enrollMessage.style.color = "#c0392b";
                enrollBtn.disabled = false;
            }
        } catch (error) {
            enrollMessage.textContent = "Could not reach the server.";
            enrollMessage.style.color = "#c0392b";
            enrollBtn.disabled = false;
        }
    });
}

/* ================= MY PROGRESS ================= */

const progressContainer = document.getElementById("progress-container");

if (progressContainer) {
    const token = localStorage.getItem("access_token");

    (async function loadProgress() {
        try {
            const enrollRes = await fetch("http://127.0.0.1:5000/api/enrollments/my", {
                headers: { "Authorization": "Bearer " + token }
            });
            const enrollData = await enrollRes.json();

            if (!enrollData.courses || enrollData.courses.length === 0) {
                progressContainer.innerHTML = "<p>You are not enrolled in any courses yet.</p>";
                return;
            }

            const progressResults = await Promise.all(
                enrollData.courses.map(function(enrollment) {
                    return fetch("http://127.0.0.1:5000/api/courses/" + enrollment.course_id + "/progress", {
                        headers: { "Authorization": "Bearer " + token }
                    }).then(function(res) { return res.json(); });
                })
            );

            progressContainer.innerHTML = "";

            enrollData.courses.forEach(function(enrollment, index) {
                const progress = progressResults[index].data;

                const item = document.createElement("div");
                item.className = "progress-item";
                item.innerHTML =
                    "<h3>" + enrollment.course_title + "</h3>" +
                    "<div class='progress-bar-bg'>" +
                        "<div class='progress-bar-fill' style='width: " + progress.progress_percentage + "%;'></div>" +
                    "</div>" +
                    "<p>" + progress.progress_percentage + "% complete (" + progress.completed_lessons + " of " + progress.total_lessons + " lessons)</p>";

                progressContainer.appendChild(item);
            });
        } catch (error) {
            progressContainer.innerHTML = "<p>Could not load progress.</p>";
        }
    })();
}

/* ================= COURSE CERTIFICATE CHECK ================= */

const viewCertificateBtn = document.getElementById("view-certificate-btn");
const certificateMessage = document.getElementById("certificate-message");

if (viewCertificateBtn && certificateMessage) {

    const actualCourseId = getCourseIdFromUrl();
    const token = localStorage.getItem("access_token");

    viewCertificateBtn.addEventListener("click", function () {
        if (!token) {
            certificateMessage.textContent = "Please login first.";
            return;
        }

        if (!actualCourseId) {
            certificateMessage.textContent = "Course information not found.";
            return;
        }

        window.location.href = "certificate.html?course_id=" + actualCourseId;
    });
}


/* ================= COURSE CONTENT ================= */

const courseContentElement =document.getElementById("course-content");

if (courseContentElement) {
    const token = localStorage.getItem("access_token");
    const params = new URLSearchParams(window.location.search);

    const courseId = getCourseIdFromUrl();

    const progressElement = document.getElementById("course-progress");

        if (progressElement && courseId && token) {
            fetch(API_BASE_URL + "/api/courses/" + courseId + "/progress", {
            headers: { "Authorization": "Bearer " + token }
            })
            .then(r => r.json())
            .then(data => {
            const percent = Number(data.progress_percentage || data.progress || 0);
            progressElement.textContent = "Progress: " + percent + "%";
            })
            .catch(() => {
            progressElement.textContent = "Could not load progress.";
            });
        }

    function escapeHtml(value) {
        return String(value || "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    async function apiRequest(path, options = {}) {
        const response = await fetch(
            API_BASE_URL + path,
            {
                ...options,
                headers: {
                    ...(token
                        ? {
                            "Authorization":
                                "Bearer " + token
                        }
                        : {}),
                    ...(options.headers || {})
                }
            }
        );

        const data = await response.json().catch(function () {
            return {};
        });

        if (!response.ok) {
            throw new Error(
                data.message ||
                "Request failed with status " +
                response.status
            );
        }

        return data;
    }

    async function loadMaterials(lessonId) {
        const result = await apiRequest(
            "/api/lessons/" +
            lessonId +
            "/materials"
        );

        return result.materials || result.data || [];
    }

    async function loadLessons(moduleId) {
        const result = await apiRequest(
            "/api/modules/" +
            moduleId +
            "/lessons"
        );

        return result.lessons || result.data || [];
    }

    function renderMaterials(materials) {
        if (!materials.length) {
            return "<p class='no-materials'>No materials available.</p>";
        }

        return `
            <div class="lesson-materials">
                <strong>Materials:</strong>
                <ul>
                    ${materials.map(function (material) {
                        const fileUrl =
                            material.file_path
                                ? API_BASE_URL +
                                  material.file_path
                                : "";

                        return `
                            <li>
                                ${escapeHtml(
                                    material.material_name
                                )}
                                ${
                                    fileUrl
                                        ? `
                                    <a
                                        href="${escapeHtml(
                                            fileUrl
                                        )}"
                                        target="_blank"
                                        rel="noopener">
                                        Open
                                    </a>
                                    `
                                        : ""
                                }
                            </li>
                        `;
                    }).join("")}
                </ul>
            </div>
        `;
    }

    async function renderLessons(moduleId) {
        const lessons = await loadLessons(moduleId);

        if (!lessons.length) {
            return "<p>No lessons available.</p>";
        }

        const lessonHtml = await Promise.all(
            lessons.map(async function (lesson) {
                let materials = [];

                try {
                    materials = await loadMaterials(
                        lesson.lesson_id
                    );
                } catch (error) {
                    console.error(
                        "Material loading error:",
                        error
                    );
                }

                return `
                    <div class="course-lesson">
                        <h4>
                            Lesson ${escapeHtml(
                                lesson.lesson_order
                            )}:
                            ${escapeHtml(
                                lesson.lesson_name
                            )}
                        </h4>

                        <p>
                            ${escapeHtml(
                                lesson.description
                            )}
                        </p>

                        ${renderMaterials(materials)}

                        <button
                            type="button"
                            class="complete-lesson-btn"
                            data-lesson-id="${
                                lesson.lesson_id
                            }">
                            Mark Lesson Complete
                        </button>

                        <span
                            class="lesson-status"
                            data-status-for="${
                                lesson.lesson_id
                            }">
                        </span>
                    </div>
                `;
            })
        );

        return lessonHtml.join("");
    }

    async function loadCourseContent() {
        if (!courseId) {
            courseContentElement.innerHTML =
                "<p>Course ID was not found.</p>";
            return;
        }

        if (!token) {
            courseContentElement.innerHTML =
                "<p>Please log in to view course content.</p>";
            return;
        }

        courseContentElement.innerHTML =
            "<div class='loading-state'><span class='spinner'></span>Loading courses...</div>";

        try {
            const result = await apiRequest(
                "/api/courses/" +
                courseId +
                "/modules"
            );

            const modules =
                result.modules ||
                result.data ||
                [];

            if (!modules.length) {
                courseContentElement.innerHTML =
                    "<p>No modules are available.</p>";
                return;
            }

            const moduleHtml = await Promise.all(
                modules.map(async function (module) {
                    let lessonsHtml =
                        "<p>Loading lessons...</p>";

                    try {
                        lessonsHtml =
                            await renderLessons(
                                module.module_id
                            );
                    } catch (error) {
                        console.error(
                            "Lesson loading error:",
                            error
                        );

                        lessonsHtml =
                            "<p>Unable to load lessons.</p>";
                    }

                    return `
                        <article class="course-module">
                            <h3>
                                Module ${escapeHtml(
                                    module.module_order
                                )}:
                                ${escapeHtml(
                                    module.module_name
                                )}
                            </h3>

                            <p>
                                ${escapeHtml(
                                    module.description
                                )}
                            </p>

                            <div class="lesson-list">
                                ${lessonsHtml}
                            </div>
                        </article>
                    `;
                })
            );

            courseContentElement.innerHTML =
                moduleHtml.join("");
        } catch (error) {
            console.error(
                "Course content loading error:",
                error
            );

            courseContentElement.innerHTML =
                "<p>Unable to load course content: " +
                escapeHtml(error.message) +
                "</p>";
        }
    }

    courseContentElement.addEventListener(
        "click",
        async function (event) {
            const completeButton =
                event.target.closest(
                    ".complete-lesson-btn"
                );

            if (!completeButton) {
                return;
            }

            const lessonId =
                completeButton.dataset.lessonId;

            const statusElement =
                document.querySelector(
                    "[data-status-for='" +
                    lessonId +
                    "']"
                );

            completeButton.disabled = true;
            completeButton.textContent =
                "Saving...";

            try {
                await apiRequest(
                    "/api/lessons/" +
                    lessonId +
                    "/complete",
                    {
                        method: "POST"
                    }
                );

                completeButton.textContent =
                    "Completed";

                if (statusElement) {
                    statusElement.textContent =
                        " ✓";
                    statusElement.style.color =
                        "#27ae60";
                }
            } catch (error) {
                completeButton.disabled = false;
                completeButton.textContent =
                    "Mark Lesson Complete";

                if (statusElement) {
                    statusElement.textContent =
                        " " + error.message;
                    statusElement.style.color =
                        "#c0392b";
                }
            }
        }
    );

    loadCourseContent();
}

/* ================================
   NOTIFICATION MODULE
================================ */

const notificationAPI = "http://localhost:5000/api/notifications";

async function loadNotifications() {
    const token = localStorage.getItem("access_token");
    const list = document.getElementById("notification-list");

    if (!list) return;

    if (!token) {
        list.innerHTML =
            "<li class='notification-item'>Please login to view notifications.</li>";
        return;
    }

    try {
        const response = await fetch(notificationAPI, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Failed to load notifications");
        }

        const notifications = result.data || [];

        if (notifications.length === 0) {
            list.innerHTML =
                "<li class='notification-item'>No notifications available.</li>";
            return;
        }

        list.innerHTML = "";

        notifications.forEach(notification => {
            const item = document.createElement("li");

            item.className = "notification-item";

            if (!notification.is_read) {
                item.classList.add("unread");
            }

            item.innerHTML = `
                <strong>${notification.title}</strong>
                <p>${notification.message}</p>
                <small>${notification.created_at || ""}</small>

                <div>
                    ${
                        !notification.is_read
                        ? `<button onclick="markNotificationAsRead(${notification.notification_id})">
                             Mark as Read
                           </button>`
                        : "<span>Read</span>"
                    }

                    <button onclick="deleteNotification(${notification.notification_id})">
                        Delete
                    </button>
                </div>
            `;

            list.appendChild(item);
        });

    } catch (error) {
        console.error("Notification error:", error);

        list.innerHTML =
            "<li class='notification-item'>Unable to load notifications.</li>";
    }
}


async function markNotificationAsRead(notificationId) {
    const token = localStorage.getItem("access_token");

    try {
        const response = await fetch(
            `${notificationAPI}/${notificationId}/read`,
            {
                method: "PATCH",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.ok) {
            loadNotifications();
        }

    } catch (error) {
        console.error("Mark notification as read error:", error);
    }
}


async function markAllNotificationsAsRead() {
    const token = localStorage.getItem("access_token");

    try {
        const response = await fetch(
            `${notificationAPI}/read-all`,
            {
                method: "PATCH",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.ok) {
            loadNotifications();
        }

    } catch (error) {
        console.error("Mark all notifications error:", error);
    }
}


async function deleteNotification(notificationId) {
    const token = localStorage.getItem("access_token");

    try {
        const response = await fetch(
            `${notificationAPI}/${notificationId}`,
            {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        if (response.ok) {
            loadNotifications();
        }

    } catch (error) {
        console.error("Delete notification error:", error);
    }
}

document.addEventListener("DOMContentLoaded", loadNotifications);

/* ================= STUDENT DASHBOARD (Feature: dashboard stats) ================= */

const studentCoursesList = document.getElementById("student-courses-list");

if (studentCoursesList) {
    const token = localStorage.getItem("access_token");

    async function loadStudentDashboard() {
        if (!token) {
            studentCoursesList.innerHTML = "<p>Please <a href='index.html'>log in</a> to see your dashboard.</p>";
            const certCount = document.getElementById("certificates-count");
            if (certCount) certCount.textContent = "";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/dashboard/student", {
                headers: { "Authorization": "Bearer " + token }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                studentCoursesList.innerHTML = "<p>" + (data.message || "Could not load dashboard.") + "</p>";
                return;
            }

            const courses = data.data.courses;
            const enrolledEl = document.getElementById("enrolled-courses-count");
            const completedEl = document.getElementById("completed-courses-count");
            const pendingEl = document.getElementById("pending-assignments-count");
            const certEarnedEl = document.getElementById("certificates-earned-count");

            if (enrolledEl) enrolledEl.textContent = courses.length;
            if (completedEl) completedEl.textContent = courses.filter(function(c) { return c.status === "COMPLETED"; }).length;
            if (pendingEl) {
                const pending = courses.reduce(function(sum, c) { return sum + (c.assignments.total - c.assignments.completed); }, 0);
                pendingEl.textContent = pending;
            }
            if (certEarnedEl) certEarnedEl.textContent = data.data.certificates;

            studentCoursesList.innerHTML = "";

            if (courses.length === 0) {
                studentCoursesList.innerHTML = "<p>You are not enrolled in any course yet. <a href='courses.html'>Browse courses</a>.</p>";
            } else {
                courses.forEach(function(course) {
                    const card = document.createElement("div");
                    card.className = "course-card";
                    card.innerHTML =
                        "<h3>" + course.course_title + "</h3>" +
                        "<p>Course ID: " + course.course_id + "</p>" +
                        "<p>Status: " + course.status + "</p>" +
                        "<p>Progress: " + course.progress + "%</p>" +
                        "<p>Assignments: " + course.assignments.completed + " / " + course.assignments.total + " evaluated</p>" +
                        "<div class='progress-bar-bg' style='max-width: 200px;'>" +
                            "<div class='progress-bar-fill' style='width: " + course.progress + "%;'></div>" +
                        "</div>";
                    studentCoursesList.appendChild(card);
                });
            }

            const certCount = document.getElementById("certificates-count");
            if (certCount) {
                certCount.textContent = "You have " + data.data.certificates + " certificate" + (data.data.certificates === 1 ? "" : "s") + ".";
            }
        } catch (error) {
            studentCoursesList.innerHTML = "<p>Could not reach the server.</p>";
        }
    }

    loadStudentDashboard();
}


/* ================= TRAINER DASHBOARD STATS (Feature: dashboard stats) ================= */

const myCoursesCount = document.getElementById("my-courses-count");

if (myCoursesCount) {
    const token = localStorage.getItem("access_token");

    async function loadTrainerDashboard() {
        if (!token) return;

        try {
            const response = await fetch("http://127.0.0.1:5000/api/dashboard/trainer", {
                headers: { "Authorization": "Bearer " + token }
            });

            const data = await response.json();

            if (!response.ok || !data.success) return;

            const stats = data.data;

            myCoursesCount.textContent = stats.total_courses;
            document.getElementById("my-students-count").textContent = stats.total_students;
            document.getElementById("pending-review-count").textContent = stats.pending_submissions;
            document.getElementById("avg-rating").textContent = stats.average_rating;
        } catch (error) {
            console.log("Could not load trainer dashboard stats:", error);
        }
    }

    loadTrainerDashboard();
}


/* ================= MY STUDENTS (Trainer) ================= */

const studentsTableBody = document.getElementById("students-table-body");

if (studentsTableBody) {
    const token = localStorage.getItem("access_token");

    async function loadMyStudents() {
        if (!token) {
            studentsTableBody.innerHTML = "<tr><td colspan='4'>Please <a href='index.html'>log in</a> as a trainer.</td></tr>";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/dashboard/trainer/students", {
                headers: { "Authorization": "Bearer " + token }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                studentsTableBody.innerHTML = "<tr><td colspan='4'>" + (data.message || "Could not load students.") + "</td></tr>";
                return;
            }

            const students = data.data.students;

            studentsTableBody.innerHTML = "";

            if (students.length === 0) {
                studentsTableBody.innerHTML = "<tr><td colspan='4'>No students enrolled in your courses yet.</td></tr>";
                return;
            }

            students.forEach(function(student) {
                const row = document.createElement("tr");

                const statusBadgeClass = student.status === "ACTIVE" ? "status-published" : "status-draft";

                row.innerHTML =
                    "<td>" + student.student_name + "</td>" +
                    "<td>" + student.course_title + "</td>" +
                    "<td>" +
                        "<div class='progress-bar-bg' style='max-width: 150px;'>" +
                            "<div class='progress-bar-fill' style='width: " + student.progress + "%;'></div>" +
                        "</div>" +
                        " " + student.progress + "%" +
                    "</td>" +
                    "<td><span class='status-badge " + statusBadgeClass + "'>" + student.status + "</span></td>";

                studentsTableBody.appendChild(row);
            });
        } catch (error) {
            studentsTableBody.innerHTML = "<tr><td colspan='4'>Could not reach the server.</td></tr>";
        }
    }

    loadMyStudents();
}


/* ================= COURSE DETAILS: ASSIGNMENT LINKS ================= */

const assignmentLinks = document.getElementById("assignment-links");

if (assignmentLinks) {
    const token = localStorage.getItem("access_token");
    const courseId = getCourseIdFromUrl();

    (async function loadAssignmentLinks() {
        if (!courseId) {
            assignmentLinks.innerHTML = "<p>Open this page from a course card to see its assignments.</p>";
            return;
        }

        if (!token) {
            assignmentLinks.innerHTML = "<p><a href='index.html'>Log in</a> to see this course's assignments.</p>";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/courses/" + courseId + "/assignments", {
                headers: { "Authorization": "Bearer " + token }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                assignmentLinks.innerHTML = "<p>" + (data.message || "Could not load assignments.") + "</p>";
                return;
            }

            const assignments = data.data;

            if (!assignments || assignments.length === 0) {
                assignmentLinks.innerHTML = "<p>No assignments for this course yet.</p>";
                return;
            }

            assignmentLinks.innerHTML = "";

            assignments.forEach(function(assignment) {
                const link = document.createElement("a");
                link.href = "assignment-submit.html?assignment=" + assignment.assignment_id;
                link.innerHTML = "<button type='button'>Submit Assignment: " + assignment.title + "</button>";
                assignmentLinks.appendChild(link);
            });
        } catch (error) {
            assignmentLinks.innerHTML = "<p>Could not reach the server.</p>";
        }
    })();
}

/* ================= ADMIN DASHBOARD STATS (Feature: dashboard stats) ================= */

const totalStudentsEl = document.getElementById("total-students");

if (totalStudentsEl && document.querySelector("nav h2") && document.querySelector("nav h2").textContent.includes("Admin")) {
    const token = localStorage.getItem("access_token");

    (async function loadAdminDashboard() {
        try {
            const response = await fetch("http://127.0.0.1:5000/api/dashboard/admin", {
                headers: { "Authorization": "Bearer " + token }
            });
            const data = await response.json();

            if (response.ok && data.success) {
                const stats = data.data;
                document.getElementById("total-students").textContent = stats.total_students;
                document.getElementById("total-trainers").textContent = stats.total_trainers;
                document.getElementById("total-courses").textContent = stats.total_courses;
                document.getElementById("published-courses").textContent = stats.published_courses;
                document.getElementById("pending-approvals").textContent = stats.pending_approvals;
                document.getElementById("total-enrollments").textContent = stats.total_enrollments;
                document.getElementById("completion-rate").textContent = stats.overall_completion_rate + "%";
            }
        } catch (error) {
            console.log("Could not load admin dashboard stats:", error);
        }
    })();
}

const dashboardNotificationsList = document.getElementById("dashboard-notifications-list");

if (dashboardNotificationsList) {
    const token = localStorage.getItem("access_token");

    (async function loadDashboardNotifications() {
        if (!token) {
            dashboardNotificationsList.innerHTML = "<li>Please log in.</li>";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/api/notifications", {
                headers: { "Authorization": "Bearer " + token }
            });
            const result = await response.json();

            const notifications = (result.data || []).slice(0, 5);

            if (!response.ok || notifications.length === 0) {
                dashboardNotificationsList.innerHTML = "<li>No new notifications.</li>";
                return;
            }

            dashboardNotificationsList.innerHTML = "";

            notifications.forEach(function(n) {
                const li = document.createElement("li");
                li.className = "notification-item" + (n.is_read ? "" : " unread");
                li.innerHTML = "<strong>" + n.title + "</strong><p>" + n.message + "</p>";
                dashboardNotificationsList.appendChild(li);
            });
        } catch (error) {
            dashboardNotificationsList.innerHTML = "<li>Unable to load notifications.</li>";
        }
    })();
}