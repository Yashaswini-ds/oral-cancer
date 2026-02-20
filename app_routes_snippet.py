@app.route('/appointments')
@login_required
def appointments():
    if current_user.role == 'doctor':
        # Doctors can see all their appointments
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    else:
        # Patients can see all their appointments
        appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
        
    return render_template('appointments.html', appointments=appointments)

@app.route('/api/appointments')
@login_required
def get_appointments():
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = Appointment.query
    if current_user.role == 'doctor':
        query = query.filter_by(doctor_id=current_user.id)
    else:
         query = query.filter_by(patient_id=current_user.id)
         
    if start and end:
        # Filter by date range if provided by FullCalendar
        # Note: start and end are ISO strings from FullCalendar
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        query = query.filter(Appointment.start_time >= start_date, Appointment.end_time <= end_date)
        
    events = []
    for apt in query.all():
        events.append({
            'id': apt.id,
            'title': f"Appointment with {apt.patient.username}" if current_user.role == 'doctor' else f"Appointment with Dr. {apt.doctor.username}",
            'start': apt.start_time.isoformat(),
            'end': apt.end_time.isoformat(),
            'extendedProps': {
                'reason': apt.reason,
                'status': apt.status,
                'patientName': apt.patient.username if apt.patient else 'Unknown',
                'doctorName': apt.doctor.username if apt.doctor else 'Unknown'
            },
            'color': '#ef4444' if apt.status == 'Cancelled' else '#10b981' if apt.status == 'Completed' else '#3b82f6'
        })
    return json.dumps(events)

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    try:
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date') # Expected format YYYY-MM-DD
        time_str = request.form.get('time') # Expected format HH:MM
        reason = request.form.get('reason')
        
        if not doctor_id or not date_str or not time_str:
             return "Missing required fields", 400
             
        # Combine date and time
        start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        # Assume 30 min duration
        end_time = start_time + timedelta(minutes=30)
        
        # Create appointment
        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=int(doctor_id),
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status='Scheduled'
        )
        db.session.add(new_appointment)
        db.session.commit()
        
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('appointments'))
    except Exception as e:
        print(f"Booking Error: {e}")
        flash("Error booking appointment.", "error")
        return redirect(url_for('appointments'))

@app.route('/cancel_appointment/<int:id>', methods=['POST'])
@login_required
def cancel_appointment(id):
    apt = Appointment.query.get_or_404(id)
    
    # Authorization check
    if current_user.id != apt.patient_id and current_user.id != apt.doctor_id:
        return "Unauthorized", 403
        
    apt.status = 'Cancelled'
    db.session.commit()
    flash("Appointment cancelled.", "info")
    return redirect(url_for('appointments'))
