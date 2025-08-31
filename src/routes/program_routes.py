from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from ..services.program_service import program_service
from datetime import datetime

program_bp = Blueprint('program', __name__)

@program_bp.route('/api/programs', methods=['POST'])
def api_create_program():
    """API endpoint to create a new program."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Program name is required'}), 400
    
    success, message, program = program_service.create_program(
        name=data['name'],
        description=data.get('description', '')
    )
    
    if success and program:
        return jsonify({
            'success': True,
            'message': message,
            'program': {
                'program_id': program.program_id,
                'name': program.name,
                'description': program.description
            }
        })
    else:
        return jsonify({'success': False, 'message': message}), 400

@program_bp.route('/api/programs/<program_id>', methods=['DELETE'])
def api_delete_program(program_id):
    """API endpoint to delete a program."""
    success, message = program_service.delete_program(program_id)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 404

@program_bp.route('/')
def index():
    """Main route that handles program selection and display."""
    program_id = request.args.get('program_id')
    
    # If no programs exist, show the new program modal
    if not program_service.get_all_programs():
        return render_template('index.html', no_programs=True)
        
    # If program_id is not provided but programs exist, use the first one
    if not program_id:
        programs = program_service.get_all_programs()
        if programs:
            return redirect(url_for('program.index', program_id=programs[0].program_id))
    
    program = program_service.get_program(program_id) if program_id else None
    if not program and program_id:
        programs = program_service.get_all_programs()
        if programs:
            return redirect(url_for('program.index', program_id=programs[0].program_id))
    
    # Get the current week number (1-6)
    current_week = (datetime.now().isocalendar()[1] - 1) % 6 + 1  # Simple week rotation
    
    return render_template(
        'index.html',
        program=program,
        programs=program_service.get_all_programs(),
        students=program.students if program else {},
        groups=program.groups if program else {},
        current_week=current_week,
        no_programs=False
    )
