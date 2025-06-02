-- Create table for storing extracted personal information
CREATE TABLE PersonalInformation (
    id INT IDENTITY(1,1) PRIMARY KEY,
    e_file_id NVARCHAR(255) NOT NULL UNIQUE,
    file_name NVARCHAR(255),
    first_name NVARCHAR(100),
    last_name NVARCHAR(100),
    email NVARCHAR(255),
    phone_number NVARCHAR(50),
    address NVARCHAR(500),
    date_of_birth DATE,
    document_type NVARCHAR(100),
    extracted_text NTEXT,
    confidence_score FLOAT,
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE()
);

-- Create index for faster searches
CREATE INDEX IX_PersonalInformation_EFileId ON PersonalInformation(e_file_id);
CREATE INDEX IX_PersonalInformation_Email ON PersonalInformation(email);
CREATE INDEX IX_PersonalInformation_CreatedDate ON PersonalInformation(created_date);