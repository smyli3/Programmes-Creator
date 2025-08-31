// Main application JavaScript

// Global state
let appState = {
    students: {},
    groups: {},
    programName: '',
    currentWeek: 1
};

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const groupContainer = document.getElementById('groupContainer');
const weekSelector = document.getElementById('weekSelector');

document.addEventListener('DOMContentLoaded', () => {
    // Initialize from server data
    const studentsData = document.getElementById('students-data');
    const groupsData = document.getElementById('groups-data');
    const programName = document.getElementById('program-name');
    
    if (studentsData) appState.students = JSON.parse(studentsData.textContent);
    if (groupsData) appState.groups = JSON.parse(groupsData.textContent);
    if (programName) appState.programName = programName.textContent;
    
    // Initialize week selector
    if (weekSelector) {
        weekSelector.value = appState.currentWeek;
        weekSelector.addEventListener('change', (e) => {
            appState.currentWeek = parseInt(e.target.value);
            renderGroups();
        });
    }
    
    // Initialize search
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                searchStudents(query);
            }, 300);
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target !== searchInput) {
                searchResults.style.display = 'none';
            }
        });
    }
    
    // Initialize groups with Sortable
    initSortableGroups();
    renderGroups();
});

// Initialize Sortable for groups and students
function initSortableGroups() {
    const groupContainers = document.querySelectorAll('.group-container');
    
    groupContainers.forEach(container => {
        new Sortable(container, {
            group: 'students',
            animation: 150,
            onEnd: handleStudentDrop,
            onAdd: handleStudentAdd,
            onRemove: handleStudentRemove
        });
    });
}

// Handle student drop event
function handleStudentDrop(evt) {
    const studentId = evt.item.dataset.studentId;
    const fromGroupId = evt.from.dataset.groupId;
    const toGroupId = evt.to.dataset.groupId;
    
    if (fromGroupId === toGroupId) return;
    
    // Update the server
    moveStudentToGroup(studentId, toGroupId);
}

// Move a student to a different group
async function moveStudentToGroup(studentId, groupId) {
    try {
        const response = await fetch(`/api/groups/${groupId}/students`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ student_id: studentId })
        });
        
        const result = await response.json();
        if (!result.success) {
            showError('Failed to move student: ' + (result.message || 'Unknown error'));
            // Revert the UI if the server update fails
            renderGroups();
        }
    } catch (error) {
        console.error('Error moving student:', error);
        showError('Failed to move student. Please try again.');
        renderGroups();
    }
}

// Handle student add to group
function handleStudentAdd(evt) {
    const studentId = evt.item.dataset.studentId;
    const groupId = evt.to.dataset.groupId;
    
    // Update the UI immediately for better UX
    const studentName = appState.students[studentId]?.name || 'Unknown Student';
    showSuccess(`${studentName} added to group`);
}

// Handle student remove from group
function handleStudentRemove(evt) {
    const studentId = evt.item.dataset.studentId;
    const groupId = evt.from.dataset.groupId;
    
    // The actual removal is handled by the drop event
}

// Search for students
async function searchStudents(query) {
    if (!query || query.length < 2) {
        searchResults.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/students/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results);
        } else {
            showError(data.message || 'Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        showError('Search failed. Please try again.');
    }
}

// Display search results
function displaySearchResults(results) {
    if (!results || results.length === 0) {
        searchResults.innerHTML = '<div class="p-2 text-muted">No matching students found</div>';
        searchResults.style.display = 'block';
        return;
    }
    
    const html = results.map(student => `
        <div class="search-result-item p-2 border-bottom" 
             data-student-id="${student.id}"
             draggable="true"
             ondragstart="onDragStart(event)">
            <div class="fw-bold">${student.name}</div>
            <small class="text-muted">
                ${student.ability} • ${student.age} years • ${student.group || 'Ungrouped'}
            </small>
        </div>
    `).join('');
    
    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
}

// Handle drag start for search results
function onDragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.studentId);
    e.dataTransfer.effectAllowed = 'move';
}

// Render all groups and students
function renderGroups() {
    if (!groupContainer) return;
    
    let html = '';
    
    // Render each group
    Object.entries(appState.groups).forEach(([groupId, group]) => {
        const students = group.student_ids.map(id => appState.students[id]).filter(Boolean);
        
        html += `
            <div class="group-card card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="group-name mb-0" contenteditable="true" 
                        data-group-id="${groupId}">${group.name}</h5>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-secondary add-note-btn" 
                                data-bs-toggle="tooltip" 
                                title="Add group note">
                            <i class="bi bi-journal-text"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-group-btn" 
                                data-group-id="${groupId}"
                                data-bs-toggle="tooltip" 
                                title="Delete group">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div class="group-container list-group list-group-flush" 
                         data-group-id="${groupId}">
                        ${students.map(student => renderStudentCard(student, groupId)).join('')}
                    </div>
                    <div class="text-center p-2 border-top">
                        <button class="btn btn-sm btn-outline-primary add-student-btn" 
                                data-group-id="${groupId}">
                            <i class="bi bi-plus"></i> Add Student
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    groupContainer.innerHTML = html;
    
    // Reinitialize event listeners
    initEventListeners();
    initSortableGroups();
}

// Render a single student card
function renderStudentCard(student, groupId) {
    if (!student) return '';
    
    const hasNotes = student.notes && student.notes.length > 0;
    const noteBadge = hasNotes ? 
        `<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
            ${student.notes.length}
        </span>` : '';
    
    return `
        <div class="student-row list-group-item d-flex justify-content-between align-items-center"
             data-student-id="${student.customer_id}"
             draggable="true">
            <div class="d-flex align-items-center">
                <div class="me-2">
                    <i class="bi bi-person-circle"></i>
                </div>
                <div>
                    <div class="fw-bold">${student.name}</div>
                    <small class="text-muted">
                        ${student.ability_level || 'Unknown'} • ${student.age || '?'} years
                    </small>
                </div>
            </div>
            <div class="btn-group">
                <button class="btn btn-sm btn-outline-primary view-notes-btn" 
                        data-student-id="${student.customer_id}"
                        data-bs-toggle="tooltip" 
                        title="View/Add Notes">
                    <i class="bi bi-journal-text"></i>
                    ${noteBadge}
                </button>
            </div>
        </div>
    `;
}

// Initialize event listeners
function initEventListeners() {
    // Group name editing
    document.querySelectorAll('.group-name').forEach(element => {
        element.addEventListener('blur', handleGroupNameEdit);
        element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.target.blur();
            }
        });
    });
    
    // Delete group buttons
    document.querySelectorAll('.delete-group-btn').forEach(button => {
        button.addEventListener('click', handleDeleteGroup);
    });
    
    // Add student buttons
    document.querySelectorAll('.add-student-btn').forEach(button => {
        button.addEventListener('click', handleAddStudent);
    });
    
    // Note buttons
    document.querySelectorAll('.view-notes-btn').forEach(button => {
        button.addEventListener('click', handleViewNotes);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Handle group name editing
async function handleGroupNameEdit(e) {
    const groupId = e.target.dataset.groupId;
    const newName = e.target.textContent.trim();
    
    if (!newName) {
        e.target.textContent = appState.groups[groupId]?.name || 'Unnamed Group';
        return;
    }
    
    try {
        const response = await fetch(`/api/groups/${groupId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: newName })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update local state
            if (appState.groups[groupId]) {
                appState.groups[groupId].name = newName;
            }
            showSuccess('Group name updated');
        } else {
            // Revert the change if the server update fails
            e.target.textContent = appState.groups[groupId]?.name || 'Unnamed Group';
            showError(result.message || 'Failed to update group name');
        }
    } catch (error) {
        console.error('Error updating group name:', error);
        e.target.textContent = appState.groups[groupId]?.name || 'Unnamed Group';
        showError('Failed to update group name. Please try again.');
    }
}

// Handle delete group
async function handleDeleteGroup(e) {
    const groupId = e.currentTarget.dataset.groupId;
    const groupName = appState.groups[groupId]?.name || 'this group';
    
    if (!confirm(`Are you sure you want to delete ${groupName}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/groups/${groupId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update local state
            delete appState.groups[groupId];
            renderGroups();
            showSuccess('Group deleted');
        } else {
            showError(result.message || 'Failed to delete group');
        }
    } catch (error) {
        console.error('Error deleting group:', error);
        showError('Failed to delete group. Please try again.');
    }
}

// Handle add student to group
function handleAddStudent(e) {
    const groupId = e.currentTarget.dataset.groupId;
    // This would open a modal or form to add a new student
    // For now, we'll just show a message
    showInfo('Add student functionality coming soon!');
}

// Handle view notes
function handleViewNotes(e) {
    const studentId = e.currentTarget.dataset.studentId;
    const student = appState.students[studentId];
    
    if (!student) {
        showError('Student not found');
        return;
    }
    
    // Create notes modal HTML
    const modalHtml = `
        <div class="modal fade" id="notesModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Notes for ${student.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="notes-list mb-3">
                            ${student.notes && student.notes.length > 0 ? 
                                student.notes.map(note => `
                                    <div class="card mb-2">
                                        <div class="card-body p-2">
                                            <div class="d-flex justify-content-between">
                                                <small class="text-muted">${new Date(note.timestamp).toLocaleString()}</small>
                                                <small class="text-muted">${note.author}</small>
                                            </div>
                                            <p class="mb-0">${note.note}</p>
                                        </div>
                                    </div>
                                `).join('') : 
                                '<p class="text-muted">No notes yet.</p>'
                            }
                        </div>
                        <div class="input-group">
                            <input type="text" class="form-control" id="newNoteInput" placeholder="Add a note...">
                            <button class="btn btn-primary" type="button" id="saveNoteBtn">
                                <i class="bi bi-send"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to DOM
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('notesModal'));
    modal.show();
    
    // Set up save note button
    document.getElementById('saveNoteBtn')?.addEventListener('click', async () => {
        const noteInput = document.getElementById('newNoteInput');
        const note = noteInput.value.trim();
        
        if (!note) return;
        
        try {
            const response = await fetch(`/api/students/${studentId}/notes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ note })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update local state
                if (!student.notes) student.notes = [];
                student.notes.push({
                    timestamp: new Date().toISOString(),
                    author: 'Instructor',
                    note: note
                });
                
                // Update the UI
                renderGroups();
                noteInput.value = '';
                
                // Show success message
                showSuccess('Note added');
            } else {
                showError(result.message || 'Failed to save note');
            }
        } catch (error) {
            console.error('Error saving note:', error);
            showError('Failed to save note. Please try again.');
        }
    });
    
    // Handle modal close
    document.getElementById('notesModal').addEventListener('hidden.bs.modal', () => {
        modal.dispose();
        document.body.removeChild(modalContainer);
    });
}

// Utility functions
function showError(message) {
    showAlert('danger', message);
}

function showSuccess(message) {
    showAlert('success', message);
}

function showInfo(message) {
    showAlert('info', message);
}

function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Add to the top of the page
    const alertContainer = document.createElement('div');
    alertContainer.innerHTML = alertHtml;
    document.body.prepend(alertContainer.firstElementChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertContainer.firstElementChild);
        if (alert) alert.close();
    }, 5000);
}

// Export for global access
window.appState = appState;
