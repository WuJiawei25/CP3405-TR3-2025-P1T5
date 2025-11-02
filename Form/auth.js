document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const lectureRole = document.getElementById('lecture-role');
    const studentRole = document.getElementById('student-role');

    lectureRole.addEventListener('click', () => {
        lectureRole.classList.add('selected');
        studentRole.classList.remove('selected');
    });
    studentRole.addEventListener('click', () => {
        studentRole.classList.add('selected');
        lectureRole.classList.remove('selected');
    });

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const isLectureSelected = lectureRole.classList.contains('selected');
        const isStudentSelected = studentRole.classList.contains('selected');
        if (isLectureSelected) {
            loginForm.action = 'A03_login_lecture.html';
        } else if (isStudentSelected) {
            loginForm.action = 'A02_login_student.html';
        } else {
            alert('Please choose your role（Lecture or Student）');
            return;
        }
        this.submit();
    });
});
