document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  document.querySelector('#send').onclick = () => {
      // Post request to send email
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject: document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value
      })
    })
    .then(response => {
      if (response.status !== 201) {
        throw response['message']
      }
      return response.json()
    })
    .then(result => {
      // Print result
       console.log(result);
       load_mailbox('sent')
    })
    .catch(error => {
      console.log(error);
      alert("Message not sent successfully!")
          return false;
    });
    return false;
  };
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    for (var i = 0; i < emails.length; i++) {
      const email = emails[i];
      const id = email['id'];
      const sender = email['sender']
      const recipients = email['recipients']
      const subject = email['subject']
      const body = email['body']
      const timestamp = email['timestamp']
      const read = email['read']
      const archived = email['archived']

      var divEmail = document.createElement('div');
      const email_link = document.createElement('button');
      email_link.innerHTML = `<button class="mail" data-id="${id}">${recipients}: ${subject} - ${timestamp}</button>`;
      divEmail.append(email_link);
      
      if (read === true) {
        divEmail.className='read-email';
      }
      else {
        divEmail.className='unread-email';
      }
      document.querySelector('#emails-view').append(divEmail);
    }
    
    document.querySelectorAll(".mail").forEach(button => {
      button.onclick = () => {
        fetch(`/emails/${button.dataset.id}`)
        .then(response => response.json())
        .then(email => show_email(email))
        .then(() => {
          if (mailbox == 'sent') {
            document.querySelector('#reply').style.display = 'none';
            document.querySelector('#archive').style.display = 'none';
            document.querySelector('#unarchive').style.display = 'none';
          }
        });
      }
    });
  })
  .catch(error => {
    console.log(error);
    alert("Messages not retrieved successfully!")
  });

}

function show_email(email) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#message-view').style.display = 'block';

  // Print email
  console.log(email);
  const id = email['id'];
  const sender = email['sender'];
  const recipients = email['recipients'];
  const subject = email['subject'];
  const body = email['body'];
  const timestamp = email['timestamp'];
  const read = email['read'];
  const archived = email['archived'];

  document.querySelector('#sender').innerHTML = `From: ${sender}`;
  document.querySelector('#recipients').innerHTML = `To: ${recipients}`;
  document.querySelector('#subject').innerHTML = `Subject: ${subject}`;
  document.querySelector('#timestamp').innerHTML = `When: ${timestamp}`;
  document.querySelector('#body').innerHTML = body;
  
  document.querySelector('#reply').addEventListener('click', () => {
    fetch(`/emails/${id}`)
        .then(response => response.json())
        .then(() => compose_email())
        .then(() => {
          // what happens to reply email?
          document.querySelector('#compose-recipients').value = sender;
          document.querySelector('#compose-subject').value = 'Re: ' + subject;
          document.querySelector('#compose-body').value = `
          On ${timestamp} ${sender} wrote:
          ${body}`;
        });
  });

  if (archived === true) {
    document.querySelector('#archive').style.display = 'none';
    document.querySelector('#unarchive').style.display = 'block';
    document.querySelector('#unarchive').dataset.id = id;
    document.querySelector('#unarchive').addEventListener('click', () => {
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: false
        })
      }).then(() => load_mailbox('inbox'));
    });
  } else {
    document.querySelector('#unarchive').style.display = 'none';
    document.querySelector('#archive').style.display = 'block';
    document.querySelector('#archive').dataset.id = id;
    document.querySelector('#archive').addEventListener('click', () => {
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: true
        })
      }).then(() => load_mailbox('inbox'));
    });
  }

  // send put request, mark as read
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  });
}
