function assignLeader() {
    const project = document.getElementById('projectSelect').value;
    const leader = document.getElementById('leaderSelect').value;
    const date = document.getElementById('assignmentDate').value;
    
    if (!project || !leader || !date) {
        alert('Please fill all required fields');
        return false;
    }
    
    // Save to localStorage (from syllabus Unit-10)
    const assignments = JSON.parse(localStorage.getItem('leaderAssignments') || '[]');
    assignments.push({
        project: project,
        leader: leader,
        date: date,
        notes: document.getElementById('assignmentNotes').value,
        timestamp: new Date().toISOString()
    });
    
    localStorage.setItem('leaderAssignments', JSON.stringify(assignments));
    
    // Show success message
    alert(`Successfully assigned ${leader.split(' ')[0]} as leader of ${project}`);
    
    // Reset form
    document.getElementById('assignLeaderForm').reset();
    
    return false; // Prevent form submission for demo
}

function removeAssignment(button) {
    if (confirm('Are you sure you want to remove this assignment?')) {
        const row = button.closest('tr');
        row.style.opacity = '0.5';
        setTimeout(() => row.remove(), 300);
    }
}