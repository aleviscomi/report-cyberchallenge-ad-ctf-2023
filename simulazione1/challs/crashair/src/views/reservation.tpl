% include('header.tpl', title='Reservation', descr='Choose the details of your reservation')

<div class="card border-secondary mb-8">
    <div class="card-header">Edit reservation</div>
    <div class="card-body">
        <form action="/reservations/{{res['ID']}}" method="post">
            <div class="custom-control custom-switch">
                <input type="checkbox" class="custom-control-input" id="seat_reservation" name="seat_reservation" {{'checked' if res['seat'] else ''}} {{'' if edit else 'disabled' }} value="1">
                <label class="custom-control-label" for="seat_reservation">Choose your seat</label>
            </div>

            <div class="custom-control custom-switch">
                <input type="checkbox" class="custom-control-input" id="online_checkin" name="online_checkin" {{'checked' if res['checkin'] else ''}} {{'' if edit else 'disabled' }} value="1">
                <label class="custom-control-label" for="online_checkin">Online check-in</label>
            </div>

            <div class="form-group">
                <label for="optional_id">Optional:</label>
                <select class="form-control" name="optional_id" id="optional_id" {{'' if edit else 'disabled' }}>
                    <option value="">--- None ---</option>
                    % for op in optionals:
                    <option value="{{ op['ID'] }}" {{'selected' if res['optional']==op['ID'] else '' }}>({{ op['ID'] }}) {{ op['type'] }} by {{ op['owner'] }} </option>
                    % end
                </select>
            </div>
            % if edit:
            <button type="submit" class="btn btn-primary form-control">Submit</button>
            % else:
            <a class="btn btn-lg btn-block btn-primary" href="/reservations" role="button">Back</a>
            % end
        </form>
    </div>
</div>

% include('footer.tpl')
