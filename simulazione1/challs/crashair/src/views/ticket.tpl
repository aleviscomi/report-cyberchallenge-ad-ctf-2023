% include('header.tpl', title='Ticket', descr='Ticket summary')

% if wait is not None:
    <div class="card border-secondary mb-8">
        <div class="card-header">Status</div>
        <div class="card-body">
            <!-- <h4 class="card-title">Secondary card title</h4> -->

            <p class="card-text">Generating ticket, please wait...</p>
            <script>
            setTimeout(function () {
                location.reload();
            }, {{ int(wait * 1000 + 100) }});
            </script>
        </div>
    </div>
% else:
    <div class="card mb-3">
        <h3 class="card-header">Ticket #{{ ticket['ticket_id'] }}</h3>
        <div class="card-body">
            <h5 class="card-title">Name of passenger</h5>
            <h6 class="card-subtitle text-muted">{{ ticket['user_id']}}</h6>
        </div>
        <div class="card-body">
            <h5 class="card-title">Can choose seat</h5>
            <h6 class="card-subtitle text-muted">{{ 'Yes' if reservation['seat'] else 'No' }}</h6>
        </div>
        <div class="card-body">
            <h5 class="card-title">Online check-in</h5>
            <h6 class="card-subtitle text-muted">{{ 'Yes' if reservation['checkin'] else 'No' }}</h6>
        </div>
        
        % if optional is not None:
        <div class="card-body">
            <h5 class="card-title">Optional</h5>
        </div>
        <ul class="list-group list-group-flush">
            <li class="list-group-item"><b>Type:</b> {{ optional['type'] }}</li>
            <li class="list-group-item"><b>Instructions:</b> {{ optional['instructions'] }}</li>
            <li class="list-group-item"><b>Private:</b> {{ 'Yes' if optional['password'] is not None else 'No' }}</li>
        </ul>
        % end
        
        <div class="card-body">
            <a href="/ticket/{{ filename_enc }}" class="card-link">Ticket link</a>
        </div>
        <div class="card-footer text-muted">
            Ticket purchased: {{ ticket['ts'] }}
        </div>
    </div>
% end

% include('footer.tpl')
