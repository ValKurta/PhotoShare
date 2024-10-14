-- Database: PhotoShare

-- DROP DATABASE IF EXISTS "PhotoShare";
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                      -- Унікальний ідентифікатор користувача. Автоматично збільшується.
    
    first_name VARCHAR(100) NOT NULL,           -- Ім'я користувача. Обов'язкове поле.
    last_name VARCHAR(100) NOT NULL,            -- Прізвище користувача. Обов'язкове поле.
    
    username VARCHAR(255) UNIQUE NOT NULL,      -- Унікальне ім'я користувача для входу в систему. Обов'язкове.
    email VARCHAR(255) UNIQUE NOT NULL,         -- Унікальний email користувача. Використовується для входу та сповіщень. Обов'язкове поле.
    
    password_hash VARCHAR(255) NOT NULL,        -- Хеш пароля для забезпечення безпеки. Сам пароль не зберігається у відкритому вигляді.
    
    phone_number VARCHAR(20),                   -- Номер телефону користувача. Необов'язкове поле, але корисне для двофакторної аутентифікації.
    
    role VARCHAR(50) CHECK (role IN ('user', 'moderator', 'admin')) DEFAULT 'user', -- Роль користувача в системі. Значення може бути 'user', 'moderator' або 'admin'.
    
    is_active BOOLEAN DEFAULT TRUE,             -- Вказує, чи активний користувач. Адміністратор може заблокувати користувача, зробивши його неактивним.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Час реєстрації користувача. Значення автоматично встановлюється при створенні користувача.
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Час останнього оновлення даних користувача. Автоматично оновлюється при зміні запису.
);

CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,                      -- Унікальний ідентифікатор кожної світлини.
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Власник світлини. Якщо користувач видаляється, його світлини також видаляються.
    url VARCHAR(255) NOT NULL,                  -- Посилання на зображення, яке зберігається у зовнішньому сервісі (Cloudinary).
    description TEXT,                           -- Опис до світлини. Необов'язкове поле.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Час завантаження світлини.
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Час останнього редагування світлини (наприклад, зміни опису).
);

CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,                      -- Унікальний ідентифікатор кожного коментаря.
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Користувач, який залишив коментар.
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE, -- Світлина, до якої залишено коментар.
    content TEXT NOT NULL,                      -- Текст коментаря. Обов'язкове поле.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Час створення коментаря.
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Час останнього редагування коментаря.
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,                      -- Унікальний ідентифікатор тега.
    name VARCHAR(50) UNIQUE NOT NULL            -- Назва тега, яка повинна бути унікальною для кожного тегу.
);

CREATE TABLE IF NOT EXISTS photo_tags (
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE, -- Світлина, до якої додається тег.
    tag_id INT REFERENCES tags(id) ON DELETE CASCADE,     -- Тег, який прив'язується до світлини.
    PRIMARY KEY (photo_id, tag_id)                        -- Композитний первинний ключ для зв'язку "багато до багатьох".
);

CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,                      -- Унікальний ідентифікатор оцінки.
    user_id INT REFERENCES users(id) ON DELETE CASCADE,  -- Користувач, який поставив оцінку.
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE, -- Світлина, яку оцінюють.
    rating INT CHECK (rating >= 1 AND rating <= 5) NOT NULL, -- Оцінка у вигляді зірок від 1 до 5.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Час створення оцінки.
);

CREATE TABLE IF NOT EXISTS transformed_photos (
    id SERIAL PRIMARY KEY,                      -- Унікальний ідентифікатор трансформованого зображення.
    photo_id INT REFERENCES photos(id) ON DELETE CASCADE, -- Вказує на оригінальну світлину.
    url VARCHAR(255) NOT NULL,                  -- Посилання на трансформоване зображення.
    qr_code_url VARCHAR(255) NOT NULL,          -- Посилання на QR-код для трансформованого зображення.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Час створення трансформованого зображення та QR-коду.
);


