function registerUser() {
    const registrationForm = document.getElementById('registration-form');
    const formData = new FormData(registrationForm);

    fetch('/api/register', {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(Object.fromEntries(formData))

    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            window.location.href = '/api/login'; 
        } else {
            console.log('Ошибка: Регистрация не выполнена');
        }
    })

}


function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
  
    const data = { username: username, password: password };
  
    fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          window.location.replace("/api");  // перенаправление пользователя на главную страницу, если вход выполнен успешно.
        } else {
          document.getElementById('error-message').innerText = data.error;  // отображение ошибки, если вход не выполнен успешно.
        }
      })
}

function getAdvertisements() {
    fetch('/api/advertisements')
    .then(response => response.json())
    .then(advertisements => {
        let advertisementList = document.getElementById('advertisement-list');
        advertisementList.innerHTML = ''; // Clear the list before adding new elements
        
        advertisements.forEach(advertisement => {
            let listItem = document.createElement('li');
            listItem.innerText = advertisement.title;
            listItem.addEventListener('click', () => showAdvertisementText(advertisement.id));
            
            advertisementList.appendChild(listItem);
        });
    });
}
function sendAdvertisement() {
    const title = document.getElementById('title').value;
    const text = document.getElementById('text').value;
    const id = document.getElementById('id').value;
  
    const advertisementData = {
      title: title,
      text_advertisement: text // Обратите внимание на правильное имя поля
    };
  
    const url = `/api/advertisements/${id}`; // Добавляем обратные кавычки
    const method = id ? 'PUT' : 'POST';
    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(advertisementData)
    })
    .then(response => {
        if (response.ok) {
          getAdvertisements();
          hideModal();
        } 
    });
}

function editAdvertisements(id, advertisementData) {
    document.getElementById('id').value = id;
    document.getElementById('title').value = advertisementData.title;
    document.getElementById('text').value = advertisementData.text_advertisement; // Обратите внимание на правильное имя поля
    showModal();
}
  
function showModal() {
    document.querySelector('div.modal').style.display = 'block';
}

function hideModal() {
    document.querySelector('div.modal').style.display = 'none';
}

function cancel() {
    hideModal();
}

function addAdvertisement() {
    document.getElementById('title').value = '';
    document.getElementById('text').value = '';
    showModal();
    document.addEventListener('DOMContentLoaded', function() {
        getAdvertisements();
    });    
}



    