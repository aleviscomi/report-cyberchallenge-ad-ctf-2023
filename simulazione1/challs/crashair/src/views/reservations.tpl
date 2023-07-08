% include('header.tpl', title='Reservation', descr='Choose the details of your reservation')

<div class="card border-secondary mb-8">
    <div class="card-header">New reservation</div>
    <div class="card-body">
        <form action="/reservations" method="post">
            <div class="custom-control custom-switch">
                <input type="checkbox" class="custom-control-input" id="seat_reservation" name="seat_reservation" checked value="1">
                <label class="custom-control-label" for="seat_reservation">Choose your seat</label>
            </div>

            <div class="custom-control custom-switch">
                <input type="checkbox" class="custom-control-input" id="online_checkin" name="online_checkin" checked value="1">
                <label class="custom-control-label" for="online_checkin">Online check-in</label>
            </div>

            <div class="form-group">
                <label for="optional_id">Optional:</label>
                <select class="form-control" name="optional_id" id="optional_id">
                    <option value="">--- None ---</option>
                    % for op in optionals:
                    <option value="{{ op['ID'] }}">({{ op['ID'] }}) {{ op['type'] }} by {{ op['owner'] }} </option>
                    % end
                </select>
            </div>

            <button type="submit" class="btn btn-primary form-control">Submit</button>
        </form>
    </div>
</div>


<table class="table">
    <thead>
        <tr>
            <th scope="col">#</th>
            <th scope="col">Author</th>
            <th scope="col">Seat Reservation</th>
            <th scope="col">Online Check-in</th>
            <th scope="col">Optional</th>
            <th scope="col">Submission Date</th>
            <th scope="col">Actions</th>
        </tr>
    </thead>
    <tbody>
        
    % for r in reservations:
    <tr class="{{ 'table-primary' if r['owner'] == username else '' }}">
        <th scope="row">{{ r['ID'] }}</th>
        <td>{{ r['owner'] }}</td>
        <td>{{ 'YES' if r['seat'] else 'NO' }}</td>
        <td>{{ 'YES' if r['checkin'] else 'NO' }}</td>
        <td>{{ '---' if r['optional'] is None else r['optional'] }}</td>
        <td>{{ r['ts'] }}</td>
        <td><a href="/reservations/{{ r['ID'] }}">{{'edit' if r['owner'] == username else 'info'}}</a></td>
    </tr>
    % end
    </tbody>
</table>

% include('footer.tpl')
