/****************** assign_leader.js ************************/


// =======================
// Assign Leader Form
// =======================
function assignLeader() {

    const project = document.getElementById('projectSelect').value;
    const leader = document.getElementById('leaderSelect').value;
    const date = document.getElementById('assignmentDate').value;

    // Basic validation
    if (!project || !leader || !date) {
        alert('Please fill all required fields');
        return false; // stop submit
    }

    // ✅ Allow normal form submit to Flask
    return true;
}


// =======================
// Remove Assignment (UI Only)
// =======================
function removeAssignment(button) {

    if (!confirm('Are you sure you want to remove this assignment?')) {
        return;
    }

    const row = button.closest('tr');

    if (row) {
        row.style.opacity = '0.5';

        setTimeout(() => row.remove(), 300);
    }
}
