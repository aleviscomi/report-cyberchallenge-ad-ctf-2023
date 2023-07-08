% include('header.tpl', title='Checkout', descr='Get your ticket')

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
            <td><a href="/checkout/{{ r['ID'] }}">checkout</a></td>
        </tr>
        % end
    </tbody>
</table>

% include('footer.tpl')
