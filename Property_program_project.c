#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>
#include <conio.h>
#include <time.h>
#include <windows.h>

// Define user structure
struct User
{
    char username[50];
    char password[50];
    char name[50];
    char lastName[50];
    char nationalCode[20];
    char phoneNumber[20];
    char email[50];
    char registrationDateTime[50];
    int count; // for (listUsersByPropertyCount) function
    struct User* next;
};

// Define a struct to hold residential property information
struct ResidentialProperty
{
    int propertyId;
    int municipalityDistrict;
    char address[100];
    char propertyType[20];
    int buildingAge;
    float areaSize;
    int floor;
    float landArea;
    char ownerPhoneNumber[20];
    int bedrooms;
    double sellingPrice;
    double mortgageAmount;
    double monthlyRentAmount;
    char registrationDate[11];  // Date of registration in the format "YYYY-MM-DD"
    char deleteDate[11];
    int isActive;  // 1 for active, 0 for inactive
    char registeredBy[50];  // Username of the user who registered the property
};

struct CommercialProperty
{
    int propertyId;
    int municipalityDistrict;
    char address[100];
    char propertyType[20];
    int buildingAge;
    float areaSize;
    int floor;
    float landArea;
    char ownerPhoneNumber[20];
    int officeRooms;
    double sellingPrice;
    double mortgageAmount;
    double monthlyRentalAmount;
    char registrationDate[11];
    char deleteDate[11];
    int isActive;
    char registeredBy[50];
};

struct LandProperty
{
    int propertyId;
    int municipalityDistrict;
    char address[100];
    char landType[20];
    float landArea;
    float distanceToMainRoad;
    int hasWell;
    char ownerPhoneNumber[20];
    double sellingPrice;
    double mortgageAmount;
    double monthlyRentAmount;
    char registrationDate[11];
    char deleteDate[11];
    int isActive;
    char registeredBy[50];
};

struct PropertyNode
{
    void* property; // مشخصه مورد نظر
    struct PropertyNode* next; // پیوند به مورد بعدی در لیست
};

// تابعی برای ایجاد یک گره جدید با مشخصات داده شده
struct PropertyNode* createPropertyNode(void* property)
{
    struct PropertyNode* newNode = malloc(sizeof(struct PropertyNode));
    newNode->property = property; // پر کردن گره جدید
    newNode->next = NULL; // پیوند نود جدید را به NULL تنظیم می‌کند
    return newNode;
}

// تابعی برای درج یک گره جدید در انتهای لیست
void insertPropertyNode(struct PropertyNode** head, void* property)
{
    struct PropertyNode* newNode = createPropertyNode(property); // ایجاد یک گره جدید
    if (*head == NULL) {
        *head = newNode; // اگر لیست خالی است، گره جدید به عنوان اولین عنصر قرار میگیرد
    } else {
        struct PropertyNode* current = *head;
        while (current->next != NULL) {
            current = current->next; // پیدا کردن آخرین عنصر در لیست
        }
        current->next = newNode; // اضافه کردن یک گره جدید به انتهای لیست
    }
}

// تابعی برای گرفتن تمام حافظه مصرف شده توسط لیست املاک و آزادسازی آن
void freePropertyList(struct PropertyNode* head)
{
    struct PropertyNode* current = head;
    while (current != NULL) {
        struct PropertyNode* temp = current;
        current = current->next;
        free(temp); // آزاد سازی تمام گره ها
    }
}

void mainMenu(struct User* currentUser);
void addInformation(struct User* currentUser);
void archive(struct User* currentUser);
void generateReports(struct User* currentUser);
void accountSettings(struct User* currentUser);
void help(const char* username);

int isValidUsername(const char* username);
int isDuplicateUsername(const char* username);
int isAlphabetic(const char* input);
int isValidPhoneNumber(const char* input);
int isValidEmail(char *email);
int isValidNationalCode(const char *code);
void hidePassword(char* password);
int isStrongPassword(char* password);
void recordFailedAttempt(const char *username);
int countFailedAttempts(const char *username);
void lockAccount(const char *username, int count);
long remainingTimeUntilUnlock(const char *username);
void removeUserAttempts(char *username);
void displayUnlockTime(long seconds);
void toLowercase(char *str);
void updateLastLoginTime(const char *username);

void registerSale(struct User* currentUser);
void registerRental(struct User* currentUser);
int getPropertyCount();
void updatePropertyCount(int newCount);
int checkAddressFormat(char address[]);
int isNumber(const char *input);
void registerResidentialPropertySale(struct User* currentUser);
void registerCommercialPropertySale(struct User* currentUser);
void registerLandSale(struct User* currentUser);
void registerResidentialPropertyRental(struct User* currentUser);
void registerCommercialPropertyRental(struct User* currentUser);
void registerLandRental(struct User* currentUser);

void deleteResidential(struct User* currentUser);
void deleteCommercial(struct User* currentUser);
void deleteLand(struct User* currentUser);
void deleteResidentialRental(struct User* currentUser);
void deleteCommercialRental(struct User* currentUser);
void deleteLandRental(struct User* currentUser);

void showNumberOfProperties(struct User *currentUser);
void listPropertiesByMunicipalArea(struct User* currentUser);
void listPropertiesByAge(struct User* currentUser);
void listPropertiesByAreaSize(struct User* currentUser);
void listPropertiesByPrice(struct User* currentUser);
void listResidentialPropertiesByBedrooms(struct User* currentUser);
void loadPropertiesFromFile(const char* filename, struct PropertyNode** propertyList);
void calculateTotalPropertyValue(struct User* currentUser);
void insertOrUpdateUser(struct User** head, const char* name, int count);
void listUsersByPropertyCount(struct User* currentUser);
void listUsersByPropertyCount(struct User* currentUser);
int calculateTimeDifference(char* lastActivity);
void listPropertiesInSpecificMarket(struct User* currentUser);
void listApartmentsByFloor(struct User* currentUser);
void listDeletedPropertiesByTimeframe(struct User* currentUser);
void listUsersAndLastActivity(struct User* currentUser);
void PropertiesRegisteredByCurrentUser(struct User *currentUser);

void viewProfile(const char* username);
int checkCurrentPassword(char* currentPassword, char* enteredUsername);
void changePassword(struct User* currentUser);
void changeName(struct User* currentUser);
void changeLastName(struct User* currentUser);
void changeEmail(struct User* currentUser);
void changePhoneNumber(struct User* currentUser);

void main()
{
    char loading[] =
    "  __        __   _                               \n\
  \\ \\      / /__| | ___ ___  _ __ ___   ___   \n\
   \\ \\ /\\ / / _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\ \n\
    \\ V  V /  __/ | (_| (_) | | | | | |  __/   \n\
     \\_/\\_/ \\___|_|\\___\\___/|_| |_| |_|\\___|  \n";

    for (int i = 0; i < sizeof(loading); i++) {
        putchar(loading[i]);
        fflush(stdout); // برای فورس کردن چاپ هر کارکتر
        usleep(1000);
    }
    menu();
}

// Function to display the menu
void menu()
{
    int choice;
    char input[100];
    printf("\n**Property Management Software**\n\n");
    printf("1. Register a new user\n");
    printf("2. Log in\n");
    printf("3. Exit the program\n");
    printf("\n>>Please choose an option: ");
    fgets(input, sizeof(input), stdin);

    if (isdigit(input[0])) // Check if the first character is a digit
    {
        sscanf(input, "%d", &choice);
        fflush(stdin);
        switch (choice)
        {
            case 1:
                system("cls");
                printf("1. Register a new user:\n\n");
                registerUser();
                break;
            case 2:
                system("cls");
                printf("2. Log in:\n\n");
                login();
                break;
            case 3:
                system("cls");
                printf("Exit the program\n\n");
                exitProgram();
                break;
            default:
                system("cls");
                printf("Invalid choice. Please try again.\n");
                menu();
                break;
        }
    }
    else
    {
        system("cls");
        printf("Invalid input. Please enter a number.\n");
        menu();
    }
}
// تابع ثبت نام
void registerUser()
{
    struct User* newUser = malloc(sizeof(struct User));
    if (newUser == NULL) {
        printf("Failed to allocate memory for the user.\n");
        exitProgram();
    }

    if (newUser != NULL)
    {
        char adminKeyPhrase[] = "RegisterAdmin";

        printf("Enter username: ");
        scanf("%s", newUser->username);

        if (strcmp(newUser->username, adminKeyPhrase) == 0)
        {
            strcpy(newUser->username, "admin");
            if(isDuplicateUsername(newUser->username))
            {
                printf("Error: Username already exists. Please choose a different username!\n");
                registerUser();
            }
            else
            {
                strcpy(newUser->name, "admin");
            }
        }
        else
        {
            toLowercase(newUser->username); // Convert the username to lowercase
            while (!isValidUsername(newUser->username) || isDuplicateUsername(newUser->username) || strcmp(newUser->username, "admin") == 0)
            {
                if (!isValidUsername(newUser->username))
                {
                printf("Invalid username format. Please enter a valid username: ");
                registerUser();

                }
                else
                {
                    printf("Error: Username already exists. Please choose a different username!\n");
                    registerUser();
                }

            }

            while (1)
            {
                printf("Enter name: ");
                scanf("%s", newUser->name);
                if (!isAlphabetic(newUser->name))
                {
                    printf("Invalid name format. Please enter a valid name.\n");
                } else
                {
                    break;
                }
            }

        }
        while (1)
        {
            printf("Enter last name: ");
            scanf("%s", newUser->lastName);

            if (!isAlphabetic(newUser->lastName)) {
                printf("Invalid last name format. Please enter a valid last name.\n");
            } else {
                break; // اگر ورودی صحیح بود از حلقه خارج می‌شود
            }
        }


        while (1)
        {
            printf("Enter phone number (09xxxxxxxxx) (11 digits): ");
            scanf("%s", newUser->phoneNumber);
            if (!isValidPhoneNumber(newUser->phoneNumber)) {
                printf("Invalid phone number format. Please enter a valid phone number.\n");
                continue;
            } else {
                break;
            }
        }

        while (1)
        {
            printf("Enter national code (10 digits): ");
            scanf("%s", newUser->nationalCode);
            if (!isValidNationalCode(newUser->nationalCode))
            {
                printf("Invalid national code format. Please enter a valid national code.\n");
            } else {
                break;
            }
        }

        while (1)
        {
            printf("Enter email: ");
            scanf("%s", newUser->email);

            if (!isValidEmail(newUser->email)) {
                printf("Invalid email format. Please enter a valid email.\n");
            } else {
                break;
            }
        }


        char password[50];
        char confirmedPassword[50];

        do {
            printf("Enter password (at least 8 characters, containing uppercase, lowercase, digit, and special character): ");
            hidePassword(password);
            if (!isStrongPassword(password))
            {
                printf("\nPassword is too weak. Please try again.\n");
                continue;
            }

            printf("\nConfirm password: ");
            hidePassword(confirmedPassword);
            printf("\n");
            if (strcmp(password, confirmedPassword) != 0) {
                printf("Passwords do not match. Please try again.\n");
            }
        } while (strcmp(password, confirmedPassword) != 0);

        FILE* userFile = fopen("users.txt", "a");
        if (userFile != NULL) {
            // نوشتن اطلاعات کاربر به فایل به همراه تاریخ و زمان ثبت نام
            char registrationDateTime[50];
            time_t t = time(NULL); //گرفتن مقدار فعلی زمان سیستم
            struct tm tm = *localtime(&t); // ذخیره به صورت یک ساختار
            sprintf(registrationDateTime, "%d-%02d-%02d-%02d:%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min);
            fprintf(userFile, "%s %s %s %s %s %s %s %s\n", newUser->username, password, newUser->name, newUser->lastName, newUser->phoneNumber, newUser->nationalCode, newUser->email, registrationDateTime);
            fclose(userFile);
            system("cls");
            printf("User registered successfully!\n");

            mainMenu(newUser->username);
        } else {
            system("cls");
            printf("Failed to register user.\n");
            getch();
        }

    free(newUser);  // آزاد سازی حافظه مختص این کاربر
    }
    else
    {
        system("cls");
        printf("Cannot register more users. The maximum number of users has been reached.\n");
    }
}
// تابع ورود
void login()
{
    char enteredUsername[50];
    char Password[50];
    char confirmedPassword[50];
    int isLoggedIn = 0;
    int attempts = 0;

    while (1)
    {
        if (attempts >= 3) //اگر سه تلاش ناموفق داشت
        {
           int count = countFailedAttempts(enteredUsername);
           if (count > 3)
            {
                count = (count / 3) * count ;
            }
           lockAccount(enteredUsername, count); //بن اکانت
           printf("Too many unsuccessful attempts. Your account is locked for %d minutes.\n" , count * 5);
           getch();
           return;
        }

        printf("Enter username: ");
        scanf("%s", enteredUsername);
        enteredUsername[strcspn(enteredUsername, "\n")] = '\0';
        toLowercase(enteredUsername);

        if (isValidUsername(enteredUsername))
        {
            long UnlockTime = remainingTimeUntilUnlock(enteredUsername);
            if (UnlockTime)
            {
                printf("Your account is locked. Please try again later.\n");
                displayUnlockTime(UnlockTime);
                getch();
                return; // برنامه را خاتمه بده
            }
        } else {
            printf("Invalid username format. Please enter a valid username.\n");
            continue;  // به ابتدای حلقه‌ی while برگرد
        }

        FILE *file = fopen("users.txt", "r");
        if (file != NULL) {
            char line[256];
            while (fgets(line, sizeof(line), file)) {
                char fileUsername[50];
                char filePassword[50];
                sscanf(line, "%s %s", fileUsername, filePassword);
                toLowercase(fileUsername);

                if (strcmp(fileUsername, enteredUsername) == 0) {
                    do {
                        printf("Enter password: ");
                        hidePassword(Password);

                        printf("\nConfirm password: ");
                        hidePassword(confirmedPassword);

                        if (strcmp(Password, confirmedPassword) != 0)
                        {
                            printf("\nPasswords do not match. Please try again.\n");
                            attempts++;
                            recordFailedAttempt(enteredUsername);
                        } else if (strcmp(filePassword, Password) != 0) {
                            printf("\nIncorrect password. Please try again.\n");
                            attempts++;
                            if (attempts >= 2)  // اگر کاربر دوبار پسوورد  را اشتباه وارد کند ، میتواند از کمک بگیرد
                            {
                                char choice;
                                printf("\n##Do you need help logging into your account? (y/n): ");
                                scanf(" %c", &choice);
                                if (choice == 'y' || choice == 'Y')
                                {
                                    system("cls");
                                    help(enteredUsername); // فراخوانی تابع یادآوری
                                }
                            }
                            recordFailedAttempt(enteredUsername);
                        } else {
                            isLoggedIn = 1;
                            break;
                        }
                    } while (attempts < 3);  // تکرار کردن عملیات تا زمانی که رمزها مطابقت داشته باشند یا تعداد تلاش‌ها به پایان برسد
                }
            }
            fclose(file);
        }

        if (isLoggedIn)
        {
            removeUserAttempts(enteredUsername);
            system("cls");
            updateLastLoginTime(enteredUsername);  // به‌روزرسانی زمان ورود
            printf("Login successful!\nWelcome %s\n", enteredUsername);
            for (int i = 0; i < 5; i++)
            {
                printf(".");
                usleep(300000); // Delay the program for 300000ms
            }
            system("cls");
            mainMenu(enteredUsername);
            break;  // اگر ورود موفقیت‌آمیز بود، از حلقه‌ی while خارج شو
        } else {
            attempts++;
            if (attempts < 3) {
                system("cls");
                printf("\nLogin failed. Incorrect username or password. Please try again.\n");
            } else {
                system("cls");
                printf("\nLogin failed.\n");
            }
        }
    }
    return;
}

// Function to exit the program
void exitProgram()
{

    printf("**Developed by Pezhman**\n\n");
    printf("Closing the program");
    // Add a delay to simulate loading time
    for (int i = 0; i < 10; i++)
    {
        printf(".");
        fflush(stdout);  // Flush the output buffer
        usleep(100000);
    }
    printf("\n");
    exit(0);
}
void mainMenu(struct User* currentUser)
{
    char input[100];  // یک رشته برای ذخیره ورودی کاربر
    int choice;
    printf("**Main Menu**\n\n");
    printf("1. Add New Information\n");
    printf("2. Delete Existing Information\n");
    printf("3. Reports\n");
    printf("4. View Profile\n");
    printf("5. Account Settings\n");
    printf("6. Logout and Return to Previous Menu\n");
    printf("\n>>Please choose an option: ");
    scanf("%s", input);

    // چک می‌کنیم که ورودی تنها شامل اعداد است یا خیر
    int validInput = 1;
    for (int i = 0; input[i] != '\0'; i++) {
        if (!isdigit(input[i])) {
            validInput = 0;
            break;
        }
    }

    if (validInput)
    {
        choice = atoi(input);  // تبدیل ورودی به عدد صحیح
        switch (choice)
        {
            case 1:
                system("cls");
                printf("Adding new information...\n\n");
                addInformation(currentUser);
                break;
            case 2:
                system("cls");
                printf("Deleting existing information...\n\n");
                archive(currentUser);
                break;
            case 3:
                system("cls");
                printf("Generating reports...\n\n");
                generateReports(currentUser);
                break;
            case 4:
                system("cls");
                viewProfile(currentUser);
                break;
            case 5:
                system("cls");
                printf("Managing account settings...\n\n");
                accountSettings(currentUser);
                break;
            case 6:
                system("cls");
                printf("Logging out...\n");
                fflush(stdin);
                menu();
                break;
            default:
                system("cls");
                printf("Invalid choice. Please try again.\n\n");
                fflush(stdin);
                mainMenu(currentUser);
                break;
        }
    } else {
        system("cls");
        printf("Invalid input. Please enter a valid option.\n\n");
        fflush(stdin);
        mainMenu(currentUser);
    }
}
// تابع انتخاب ثبت ملک جدید
void addInformation(struct User* currentUser)
{
    char input[20];
    int isValid = 0; // یک نشانه برای بررسی صحت ورودی
    int choice;
    printf("1. Register a sale\n");
    printf("2. Register a rental\n");
    printf("3. Return to previous menu\n");
    printf("\n\n>>Choose an option: ");

    while (!isValid)
    {
        scanf("%s", input);

        isValid = 1; // فرض می‌کنیم ورودی صحیح است
        for (int i = 0; input[i] != '\0'; i++)
        {
            if (!isdigit(input[i]))
            {
                isValid = 0;
                printf("Invalid input. Please enter a number: ");
                fflush(stdin);
                break;
            }
        }
    }

    choice = atoi(input);

    switch(choice)
    {
        case 1:
            system("cls");
            printf("Register a sale...\n\n");
            registerSale(currentUser);
            break;
        case 2:
            system("cls");
            printf("Register a rental...\n\n");
            registerRental(currentUser);
            break;
        case 3:
            system("cls");
            mainMenu(currentUser);
        default:
            system("cls");
            printf("Invalid choice. Please try again.\n\n");
            fflush(stdin);
            addInformation(currentUser);
            break;
    }
}
//تابع آرشیو اطلاعات املاک
void archive(struct User* currentUser)
{
    int choice;
    char input[20];
    int isValid = 0;
    printf("1. Delete residential property\n");
    printf("2. Delete commercial property\n");
    printf("3. Delete land\n");
    printf("4. Delete residential rental property\n");
    printf("5. Delete commercial rental property\n");
    printf("6. Delete land rental property\n");
    printf("7. Return to Previous Menu\n");
    printf("\n>>Please select an option: ");

    while (!isValid) {
        scanf("%s", input);

        isValid = 1;
        for (int i = 0; input[i] != '\0'; i++) {
            if (!isdigit(input[i])) {
                isValid = 0;
                printf("Invalid input. Please enter a number: ");
                fflush(stdin);
                break;
            }
        }
    }

    choice = atoi(input);

    switch (choice) {
        case 1:
            system("cls");
            printf("1. Delete residential property\n");
            deleteResidential(currentUser);
            break;
        case 2:
            system("cls");
            printf("2. Delete commercial property\n");
            deleteCommercial(currentUser);
            break;
        case 3:
            system("cls");
            printf("3. Delete land\n");
            deleteLand(currentUser);
            break;
        case 4:
            system("cls");
            printf("4. Delete residential rental property\n");
            deleteResidentialRental(currentUser);
            break;
        case 5:
            system("cls");
            printf("5. Delete commercial rental property\n");
            deleteCommercialRental(currentUser);
            break;
        case 6:
            system("cls");
            printf("6. Delete land rental property\n");
            deleteLandRental(currentUser);
            break;
        case 7:
            system("cls");
            fflush(stdin);
            mainMenu(currentUser);
            break;
        default:
            system("cls");
            printf("Invalid option\n");
            fflush(stdin);
            archive(currentUser);
            break;
    }
}
//تابع گزارش ها
void generateReports(struct User* currentUser)
{
    system("cls");
    int option;
    char input[20];
    int isValid = 0;

    printf("**Reports**\n\n");
    printf("1. Show number of properties\n");
    printf("2. List properties by municipal area\n");
    printf("3. List properties by age\n");
    printf("4. List properties by area size\n");
    printf("5. List properties by price\n");
    printf("6. List residential properties by bedrooms\n");
    printf("7. Calculate total property value\n");
    printf("8. List users by property count\n");
    printf("9. List rental properties with restrictions\n");
    printf("10. List properties in specific market\n");
    printf("11. List apartments by floor\n");
    printf("12. List deleted properties by timeframe\n");
    printf("13. List users and last activity\n");
    printf("14. Properties registered by the user\n");
    printf("15. Return to Previous Menu\n");
    printf("\n\n>>Choose an option: ");

    while (!isValid) {
        scanf("%s", input);

        isValid = 1;
        for (int i = 0; input[i] != '\0'; i++) {
            if (!isdigit(input[i])) {
                isValid = 0;
                printf("Invalid input. Please enter a number: ");
                fflush(stdin);
                break;
            }
        }
    }
    option = atoi(input);

    switch (option)
    {
        case 1:
            system("cls");
            printf("Show number of properties...\n\n");
            showNumberOfProperties(currentUser);
            break;
        case 2:
            system("cls");
            printf("List properties by municipal area...\n\n");
            listPropertiesByMunicipalArea(currentUser);
            break;
        case 3:
            system("cls");
            printf("List properties by age...\n\n");
            listPropertiesByAge(currentUser);
            break;
        case 4:
            system("cls");
            printf("List properties by area size...\n\n");
            listPropertiesByAreaSize(currentUser);
            break;
        case 5:
            system("cls");
            printf("List properties by price...\n\n");
            listPropertiesByPrice(currentUser);
            break;
        case 6:
            system("cls");
            printf("List residential properties by bedrooms...\n\n");
            listResidentialPropertiesByBedrooms(currentUser);
            break;
        case 7:
            system("cls");
            printf("Calculate total property value...\n\n");
            calculateTotalPropertyValue(currentUser);
            break;
        case 8:
            system("cls");
            printf("List users by property count...\n\n");
            listUsersByPropertyCount(currentUser);
            break;
        case 9:
            system("cls");
            printf("List rental properties with restrictions...\n\n");
            listRentalPropertiesWithRestrictions(currentUser);
            break;
        case 10:
            system("cls");
            printf("List properties in specific market...\n\n");
            listPropertiesInSpecificMarket(currentUser);
            break;
        case 11:
            system("cls");
            printf("List apartments by floor...\n\n");
            listApartmentsByFloor(currentUser);
            break;
        case 12:
            system("cls");
            printf("List deleted properties by timeframe...\n\n");
            listDeletedPropertiesByTimeframe(currentUser);
            break;
        case 13:
            system("cls");
            printf("List users and last activity...\n\n");
            listUsersAndLastActivity(currentUser);
            break;
        case 14:
            system("cls");
            printf("Properties registered by the user...\n\n");
            PropertiesRegisteredByCurrentUser(currentUser);
            break;
        case 15:
            system("cls");
            fflush(stdin);
            mainMenu(currentUser);
            break;
        default:
            printf("Invalid option\n");
            fflush(stdin);
            generateReports(currentUser);
            break;
    }
}
// تابع تنظیمات مشخصات کاربر
void accountSettings(struct User* currentUser)
{
    int choice;
    char input[20];
    int isValid = 0;

    system("cls");
    printf("1. Change password\n");
    printf("2. Change name\n");
    printf("3. Change last name\n");
    printf("4. Change phone number\n");
    printf("5. Change email\n");
    printf("6. Back to previous menu\n");
    printf("Select an option: ");

    while (!isValid)
    {
        scanf("%s", input);

        isValid = 1;
        for (int i = 0; input[i] != '\0'; i++)
        {
            if (!isdigit(input[i])) {
                isValid = 0;
                printf("Invalid input. Please enter a number: ");
                fflush(stdin);
                break;
            }
        }
    }

    choice = atoi(input);

    switch (choice)
    {
        case 1:
            system("cls");
            printf("Change password...\n\n");
            changePassword(currentUser);
            break;
        case 2:
            system("cls");
            printf("Change name...\n\n");
            changeName(currentUser);
            break;
        case 3:
            system("cls");
            printf("Change last name...\n\n");
            changeLastName(currentUser);
            break;
        case 4:
            system("cls");
            printf("Change phone number...\n\n");
            changePhoneNumber(currentUser);
            break;
        case 5:
            system("cls");
            printf("Change email...\n\n");
            changeEmail(currentUser);
            break;
        case 6:
            system("cls");
            fflush(stdin);
            mainMenu(currentUser);
            break;
        default:
            system("cls");
            printf("Invalid choice...\n\n");
            fflush(stdin);
            accountSettings(currentUser);
            break;
    }
}
// تابع ثبت اطلاعات املاک فروشی
void registerSale(struct User* currentUser)
{
    char input[20];
    int isValid = 0;
    int choice;

    printf("1. Residential property\n");
    printf("2. Commercial property\n");
    printf("3. Land\n");
    printf("4. Back to previous menu\n");
    printf("\n\n>>Choose a property type: ");

    while (!isValid) {
        scanf("%s", input);

        isValid = 1;
        for (int i = 0; input[i] != '\0'; i++)
        {
            if (!isdigit(input[i])) {
                isValid = 0;
                printf("Invalid input. Please enter a number: ");
                fflush(stdin);
                break;
            }
        }
    }

    choice = atoi(input);

    switch(choice)
    {
        case 1:
            system("cls");
            printf("Residential property\n\n");
            registerResidentialPropertySale(currentUser); // فراخوانی تابع ثبت مشخصات ملک مسکونی
            break;
        case 2:
            system("cls");
            printf("Commercial property\n\n");
            registerCommercialPropertySale(currentUser);
            break;
        case 3:
            system("cls");
            printf("Land\n\n");
            registerLandSale(currentUser);
            break;
        case 4:
            system("cls");
            fflush(stdin);
            addInformation(currentUser);
            break;
        default:
            system("cls");
            printf("Invalid choice! Please try again.\n");
            fflush(stdin);
            registerSale(currentUser);
            break;
    }
}

//تابع ثبت اطلاعات املاک اجاراه ای
void registerRental(struct User* currentUser)
{
    char input[20];
    int isValid = 0;
    int choice;

    printf("1. Residential property\n");
    printf("2. Commercial property\n");
    printf("3. Land\n");
    printf("4. Back to previous menu\n");
    printf("\n\n>>Choose a property type: ");

    while (!isValid)
    {
        scanf("%s", input);

        isValid = 1;
        for (int i = 0; input[i] != '\0'; i++)
        {
            if (!isdigit(input[i])) {
                isValid = 0;
                printf("Invalid input. Please enter a number: ");
                fflush(stdin);
                break;
            }
        }
    }

    choice = atoi(input);

    switch(choice)
    {
        case 1:
            system("cls");
            printf("Residential property...\n\n");
            registerResidentialPropertyRental(currentUser); // فراخوانی تابع ثبت مشخصات ملک مسکونی برای اجاره
            break;
        case 2:
            system("cls");
            printf("Commercial property...\n\n");
            registerCommercialPropertyRental(currentUser);
            break;
        case 3:
            system("cls");
            printf("Land...\n\n");
            registerLandRental(currentUser);
            break;
        case 4:
            system("cls");
            fflush(stdin);
            addInformation(currentUser);
            isValid = 0;
            break;
        default:
            system("cls");
            printf("Invalid choice. Please try again.\n");
            fflush(stdin);
            registerRental(currentUser);
            break;
    }
}
// این تابع برای یادآوری پسوورد است ، کاربر باید تمام مشخصات خود را صحیح وارد کند
void help(const char* username)
{
    printf("#Help Section\n");
    printf("Your username: %s\n" , username);
    for (int i = 0; i < 5; i++)
    {
        printf(".");
        usleep(300000);
    }
    printf("\nIf you need assistance, please enter all your account information correctly.\n");

    char Ename[50];
    char ElastName[50];
    char EphoneNumber[50];
    char EnationalCode[50];
    char Eemail[50];

    printf("Enter name: ");
    scanf("%49s", Ename);
    printf("Enter lastName: ");
    scanf("%49s", ElastName);
    printf("Enter phoneNumber: ");
    scanf("%49s", EphoneNumber);
    printf("Enter nationalCode: ");
    scanf("%49s", EnationalCode);
    printf("Enter email: ");
    scanf("%49s", Eemail);

    FILE* originalFile = fopen("users.txt", "r");
    if (originalFile != NULL) {
        char user[50];
        char name[50];
        char lastName[50];
        char phoneNumber[50];
        char nationalCode[50];
        char email[50];
        char password[50];
        char lastLogin[50];

        int found = 0;

        while (fscanf(originalFile, "%s %s %s %s %s %s %s %s\n",
                      user, password, name, lastName, phoneNumber, nationalCode, email, lastLogin) == 8) {
            if (strcmp(username, user) == 0 &&
                strcmp(Ename, name) == 0 &&
                strcmp(ElastName, lastName) == 0 &&
                strcmp(EphoneNumber, phoneNumber) == 0 &&
                strcmp(EnationalCode, nationalCode) == 0 &&
                strcmp(Eemail, email) == 0)
            {
            // نمایش دو رقم اول وآخر پسوورد کاربر برای یادآوری
                printf("\nYour password is: %c%c****%c%c\n\n", password[0], password[1], password[strlen(password) - 2], password[strlen(password) - 1]);
                printf("Now ");
                found = 1;
                break;
            }
        }

        if (!found) {
            printf("Error: User information not found or does not match.\n");
        }

        fclose(originalFile);
    } else {
        printf("Error: Failed to open user file.\n");
    }
}
// تابع بررسی صحت نام کاربری
int isValidUsername(const char* username)
{
    int i;
    int length = strlen(username);

    // Check the length of the username
    if (length < 4 || length > 50) {
        return 0;
    }

    // Check each character in the username for validity
    for (i = 0; i < length; i++) {
        if (!(isalnum(username[i]) || username[i] == '_' || username[i] == '.')) {
            return 0;
        }
    }

    return 1; // If the username is valid
}

// Function to check if the input contains only alphabetic characters
int isAlphabetic(const char* input)
{
    for (int i = 0; input[i] != '\0'; i++)
    {
        if (!isalpha(input[i]))
        {
            return 0;
        }
    }
    return 1;
}

// Function to check if the input is a valid phone number
int isValidPhoneNumber(const char* input)
{
    if (strlen(input) != 11 || strncmp(input, "09", 2) != 0)
    {
        return 0; // نامعتبر
    }
    for (int i = 0; i < 11; i++)
    {
        if (i < 2)
        {
            continue; // Skip the first two characters
        }
        if (!isdigit(input[i]))
        {
            return 0;
        }
    }
    return 1;
}

// Function to check if the input is a valid email address
int isValidEmail(char *email)
{
    int emailLength = strlen(email);
    int atPosition = -1;
    int dotPosition = -1;
    int i;

    if (emailLength < 6) {
        return 0; // Email address is not valid
    }

    // Checking for the existence of @ and dot in the email
    for (i = 0; i < emailLength; i++)
    {
        if (email[i] == '@')
        {
            atPosition = i; // Save the position of @
        }
        else if (email[i] == '.')
        {
            dotPosition = i; // Save the position of dot
        }
    }

    // If @ and dot exist, and the position of dot is greater than @, the email address is valid
    if (atPosition > 0 && dotPosition > atPosition && dotPosition < emailLength - 1
        && email[0] != '.' && email[atPosition + 1] != '.')
    {
        return 1; // Email address is valid
    }
    else
    {
        return 0;
    }
}

// Function to check the validity of the national code
int isValidNationalCode(const char *code)
{
    if (strlen(code) != 10)
    {
        return 0; // نامعتبر
    }
    for (int i = 0; i < 10; i++) {
        if (!isdigit(code[i])) {
            return 0;
        }
    }
    return 1;
}
// تابع برای نمایش ستاره هنگام وارد کردن پسوورد
void hidePassword(char* password)
{
    int i = 0;
    while (1) {
        char c = getch();
        if (c != 9 && c != 27 , c != 32 ,c != 127 )
            {
            if (c == '\r' || c == '\n') {
                if (i >= 8) {
                    password[i] = '\0';
                    break;
                }
            } else if (i > 0) {
                if (c == 8) {
                    printf("\b \b");
                    password[i - 1] = '\0';
                    i--;
                } else {
                    printf("%c", c);
                    usleep(100000);
                    printf("\b \b");
                    password[i] = c;
                    printf("*");
                    i++;
                }
            } else {
                if (c != 8) {
                    password[i] = c;
                    printf("*");
                    i++;
                }
            }
        }
    }
}

int isDuplicateUsername(const char* username)
{
    FILE* file = fopen("users.txt", "a+");
    if (file == NULL)
    {
        printf("Error opening files\n");
        exit(1);
    }

    char fileUsername[50];
    while (fscanf(file, "%s", fileUsername) != EOF)
    {
        if (strcmp(fileUsername, username) == 0)
        {
            fclose(file);
            return 1;  // Username already exists in the file
        }
    }

    fclose(file);
}

int isStrongPassword(char* password)
{
    int length = 0, hasUpperCase = 0, hasLowerCase = 0, hasDigit = 0, hasSpecialChar = 0;
    while (password[length] != '\0')
    {
        if (isupper(password[length]))
        {
            hasUpperCase = 1;
        }
        else if (islower(password[length]))
        {
            hasLowerCase = 1;
        }
        else if (isdigit(password[length]))
        {
            hasDigit = 1;
        } else if (ispunct(password[length]))
        {
            hasSpecialChar = 1;
        }
        length++;
    }
    if (length < 8 || !hasUpperCase || !hasLowerCase || !hasDigit || !hasSpecialChar || strchr(password, ' ') != NULL)
    {
        return 0; // خروجی ۰ برای پسوردهای ضعیف یا شامل space است
    }
    return 1; // در غیر اینصورت، پسورد قوی است
}


void recordFailedAttempt(const char *username) // تابع برای ذخیره تلاش های ناموفق
{
    FILE *file = fopen("failed_attempts.txt", "a");
    if (file != NULL) {
        fprintf(file, "%s\n", username);
        fclose(file);
    } else {
        printf("Error recording failed attempt for user: %s\n", username);
    }
}

int countFailedAttempts(const char *username) // تابع برای شمارش تعداد تلاش های ناموفق
{
    FILE *file = fopen("failed_attempts.txt", "r");
    int count = 0;
    if (file != NULL) {
        char line[100];
        while (fgets(line, sizeof(line), file))
        {
            if (strstr(line, username) != NULL)
            {
                count++;
            }
        }
        fclose(file);
        return count;
    }
    else
    {
        printf("Error opening failed_attempts.txt\n");
        return -1;
    }
}

void lockAccount(const char *username, int count) // تابع برای بن اکانت
{
    FILE *lockFile = fopen(username, "w");
    if (lockFile != NULL) {
        time_t unlockTime = time(NULL) + (count * 5 * 60); // زمان قفل اکانت
        fprintf(lockFile, "%ld", unlockTime);
        fclose(lockFile);
    } else {
        printf("Error locking the account for user: %s\n", username);
    }
}

long remainingTimeUntilUnlock(const char *username) // تابع برای محاسبه اینکه چه زمانی محدودیت کاربر برداشته میشود
{
    FILE *lockFile = fopen(username, "r");
    if (lockFile != NULL) {
        long unlockTime;
        if (fscanf(lockFile, "%ld", &unlockTime) == 1)
        {
            fclose(lockFile);
            long remainingTime = unlockTime - time(NULL);
            if (remainingTime > 0) {
                return remainingTime;
            } else {
                remove(username);  // Remove lock file if the lock time has ended
                return 0;  // Account is not locked anymore
            }
        } else {
            fclose(lockFile);
            return 0;  // Account is not locked anymore
        }
    }
    return 0;  // Account is not locked
}

void removeUserAttempts(char *username)
{
    FILE *file = fopen("failed_attempts.txt", "r");
    char *tmpFileName = "temp_failed_attempts.txt";
    FILE *tempFile = fopen(tmpFileName, "w");
    char line[100];

    if (file == NULL || tempFile == NULL)
    {
        printf("Error opening files\n");
        return;
    }

    while (fgets(line, sizeof(line), file)) {
        line[strcspn(line, "\n")] = 0;  //remove newline character
        if (strcmp(line, username) != 0) {
            fprintf(tempFile, "%s\n", line);
        }
    }

    fclose(file);
    fclose(tempFile);

    remove("failed_attempts.txt");
    rename(tmpFileName, "failed_attempts.txt");
}

void displayUnlockTime(long seconds) // نمایش زمان محدودیت برای کاربر
{
    time_t unlockTime = time(NULL) + seconds;

    struct tm *unlockTimeStruct = localtime(&unlockTime);
    printf("Unlock Time: %d-%02d-%02d %02d:%02d\n", unlockTimeStruct->tm_year + 1900, unlockTimeStruct->tm_mon + 1, unlockTimeStruct->tm_mday, unlockTimeStruct->tm_hour, unlockTimeStruct->tm_min);
}

void toLowercase(char *str)
{
    // تبدیل تمام حروف رشته به حروف کوچک
    for (int i = 0; str[i]; i++)
    {
        if (isalpha(str[i]))  // بررسی آیا این حرف یک حرف الفباست
        {
            str[i] = tolower(str[i]);  // تبدیل حرف به حرف کوچک
        }
    }
}

void updateLastLoginTime(const char *username)
{
    // به روزرسانی زمان آخرین ورود کاربر
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    FILE *file = fopen("users.txt", "r");  // باز کردن فایل کاربران برای خواندن
    if (file != NULL) {
        FILE *tempFile = fopen("temp.txt", "w+");  // باز کردن یک فایل موقت برای نوشتن
        if (tempFile != NULL) {
            char line[256];
            while (fgets(line, sizeof(line), file)) {
                char fileUsername[50], filePassword[50], lastLogin[50], name[50], lastName[50], phoneNumber[50], nationalCode[50], email[50];
                sscanf(line, "%s %s %s %s %s %s %s %s\n", fileUsername, filePassword, name, lastName, phoneNumber, nationalCode, email, lastLogin);
                if (strcmp(fileUsername, username) == 0) { // یافتن کاربر با نام کاربری و به روزرسانی زمان ورود
                    fprintf(tempFile, "%s %s %s %s %s %s %s %d-%02d-%02d-%02d:%02d\n", fileUsername, filePassword, name, lastName, phoneNumber, nationalCode, email, tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min);
                } else {
                    fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", fileUsername, filePassword, name, lastName, phoneNumber, nationalCode, email, lastLogin);  // نوشتن اطلاعات کاربران دیگر بدون تغییر
                }
            }
            fclose(tempFile);
            fclose(file);
            remove("users.txt");  // حذف فایل اصلی
            rename("temp.txt", "users.txt");  // تغییر نام فایل موقت به نام فایل اصلی
        }
    }
}

int getPropertyCount() {
    FILE *countFile = fopen("propertyCount.txt", "r");  // باز کردن فایل شمارش ملک‌ها برای خواندن
    int count = 0;
    if (countFile != NULL)
    {
        Beep(310, 200);  // پخش صدا
        Beep(330, 60);
        Beep(350, 60);
        Beep(380, 60);
        Beep(310, 250);
        fscanf(countFile, "%d", &count);  // خواندن تعداد ملک‌ها از فایل
        fclose(countFile);
    }
    else
    {
        FILE *countFile = fopen("propertyCount.txt", "w");  // قرار دادن مقدار پیش‌فرض اگر فایل وجود نداشته باشد
        count = 0 ;
        fprintf(countFile, "%d", count);  // نوشتن مقدار پیش‌فرض
    }
    return count;
}

void updatePropertyCount(int newCount)
{
    FILE *countFile = fopen("propertyCount.txt", "w");  // باز کردن فایل شمارش ملک‌ها برای نوشتن
    if (countFile != NULL) {
        fprintf(countFile, "%d", newCount);  // ذخیره کردن تعداد ملک‌ها در فایل
        fclose(countFile);
    }
}


int checkAddressFormat(char address[])
{
    // چک کردن طول آدرس
    if (strlen(address) < 10 || strlen(address) > 100)
    {
        return 0; // فرمت نادرست
    }

    for (int i = 0; i < strlen(address); i++) {
        if (address[i] == ',') {
            return 0; // فرمت نادرست
        }
    }

    return 1; // فرمت صحیح
}
int isNumber(const char *input) {
    while (*input) {
        if (!isdigit(*input)) {
            return 0;  // ورودی شامل حرف یا نماد نیست
        }
        input++;
    }
    return 1;  // همه ی حروف ورودی عددی هستند
}

// Function to register a residential property sale
void registerResidentialPropertySale(struct User* currentUser)
{
    struct ResidentialProperty property;
    char userInput[50];
    char phoneNumber[20];
    char registrationDate[11];

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(registrationDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

    int propertyCount = getPropertyCount(); // Get current property count
    property.propertyId = propertyCount + 1;  // Generate unique property id

    updatePropertyCount(property.propertyId); // Update property count in file


    property.propertyId = propertyCount + 1;  // Generate unique property id

    // Get property information from the user
    while (1)
    {
        printf("Enter municipality district number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.municipalityDistrict = atoi(userInput);  // تبدیل ورودی به عدد صحیح
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }

    while (1)
    {
        printf("Enter exact address (Use a dash to separate): ");
        scanf(" %[^\n]s", property.address); // Allowing spaces in the address
        if (!checkAddressFormat(property.address))
        {
            printf("The format is invalid. Please enter a valid address.\n");
        } else
        {
            break;
        }
    }
    int choice;
    bool continueLoop = true; // تعیین می‌کند که حلقه باید ادامه یا خاتمه یابد
    while (continueLoop)
    {
        printf("Enter property type (1.Apartment , 2.Villa  . 3.other): ");
        scanf("%s", userInput);
        if (!isNumber(userInput)) { // بررسی معتبر بودن ورودی
            printf("Invalid input! Please enter a number.\n");
        }
        else
        {
            choice = atoi(userInput);
            switch (choice)
            {
                case 1:
                    strcpy(property.propertyType, "Apartment"); // تنظیم نوع ملک به آپارتمان
                    continueLoop = false; // پایان حلقه
                    break;
                case 2:
                    strcpy(property.propertyType, "Villa"); // تنظیم نوع ملک به ویلا
                    continueLoop = false; // پایان حلقه
                    break;
                case 3:
                    printf("Please enter the property type: "); // درخواست ورودی از کاربر برای نوع دیگر
                    scanf(" %[^\n]s", property.propertyType);
                    continueLoop = false; // پایان حلقه
                    break;
                default:
                    printf("Invalid choice, please try again.\n");
                    break;
            }
        }
    }
    while (1)
    {
        printf("Enter building age: ");
        scanf("%s", userInput);

        if (isNumber(userInput)) {
            property.buildingAge = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter area size (in square meters): ");
        if (scanf("%f", &property.areaSize) != 1)
        {
            while (getchar() != '\n'); // clear input buffer
            printf("The format is invalid . Please enter a valid area size.\n");
        } else {
            break;
        }
    }

    while (1)
    {
        printf("Enter land area (in square meters): ");
        if (scanf("%f", &property.landArea) != 1 || property.landArea < property.areaSize)
        {
            while (getchar() != '\n');
            printf("The format is invalid or land area is less than area size. Please enter a valid land area.\n");
        } else {
            break;
        }
    }

    while (1)
    {
        printf("Enter floor number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.floor = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }

    do {
        printf("Enter owner's phone number (09xxxxxxxxx): ");
        scanf(" %s", phoneNumber);
        if (!isValidPhoneNumber(phoneNumber)) {
            printf("Invalid phone number format. Please enter a valid Iranian mobile number starting with 09.\n");
        }
    } while (!isValidPhoneNumber(phoneNumber));
    strcpy(property.ownerPhoneNumber, phoneNumber);

    while (1)
    {
        printf("Enter number of bedrooms: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.bedrooms = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }

    }

    // Calculate suggested selling price based on area size
    double suggestedSellingPrice = property.areaSize * 10000000;  // assuming 10 million Toman per square meter
    printf("\n**Suggested selling price (based on area size): %.2lf\n", suggestedSellingPrice);

    while (1)
    {
        printf("Enter selling price: ");
        if (scanf("%lf", &property.sellingPrice) != 1)
        {
            while (getchar() != '\n'); // clear input buffer
            printf("The format is invalid. Please enter a valid selling price.\n");
        } else
        {
            break;
        }
    }
    // Set additional property information
    strcpy(property.registrationDate, registrationDate);  // Set the registration date
    property.isActive = 1;  // Set the property as active
    strcpy(property.registeredBy, currentUser->username);  // Set the username of the user who registered the property

    // Save property information to a file
    FILE *file = fopen("residential_properties.txt", "a");
    if (file != NULL)
    {
        fprintf(file, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%.2lf,%s\n",
                property.propertyId,
                property.isActive,
                property.registeredBy,
                property.municipalityDistrict,
                property.address,
                property.propertyType,
                property.buildingAge,
                property.areaSize,
                property.floor,
                property.landArea,
                property.ownerPhoneNumber,
                property.bedrooms,
                property.sellingPrice,
                property.registrationDate);
        fclose(file);
        printf("\n\nResidential property information saved successfully.\n");
        printf("Press any key to continue.\n");
        getch();
        fflush(stdin);
        system("cls");
        addInformation(currentUser);
    }
    else
    {
        printf("Unable to save property information to file.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    }
}

void registerCommercialPropertySale(struct User* currentUser)
{
    struct CommercialProperty property;
    char userInput[50];
    char phoneNumber[20];
    char registrationDate[11];

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(registrationDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

    int propertyCount = getPropertyCount(); // تعداد فعلی املاک
    property.propertyId = propertyCount + 1;

    updatePropertyCount(property.propertyId);


    while (1)
    {
        printf("Enter municipality district number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.municipalityDistrict = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter exact address (Use a dash to separate): ");
        scanf(" %[^\n]s", property.address);
        if (!checkAddressFormat(property.address))
        {
            printf("The format is invalid. Please enter a valid address.\n");
        } else
        {
            break;
        }
    }
    printf("Enter property type (Official document, Administrative location, etc.): ");
    scanf(" %[^\n]s", property.propertyType);
    while (1)
    {
        printf("Enter building age: ");
        scanf("%s", userInput);

        if (isNumber(userInput)) {
            property.buildingAge = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter area size (in square meters): ");
        if (scanf("%f", &property.areaSize) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid . Please enter a valid area size.\n");
        } else {
            break;
        }
    }
    while (1)
    {
        printf("Enter land area (in square meters): ");
        if (scanf("%f", &property.landArea) != 1 || property.landArea < property.areaSize) {
            while (getchar() != '\n');
            printf("The format is invalid or land area is less than area size. Please enter a valid land area.\n");
        } else {
            break;
        }
    }
    while (1)
    {
        printf("Enter floor number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.floor = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    do {
        printf("Enter owner's phone number (09xxxxxxxxx): ");
        scanf(" %s", phoneNumber);
        if (!isValidPhoneNumber(phoneNumber)) {
            printf("Invalid phone number format. Please enter a valid Iranian mobile number starting with 09.\n");
        }
    } while (!isValidPhoneNumber(phoneNumber));
    strcpy(property.ownerPhoneNumber, phoneNumber);

    while (1)
    {
        printf("Enter number of office rooms: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.officeRooms = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }

    }
    while (1)
    {
        printf("Enter selling price: ");
        if (scanf("%lf", &property.sellingPrice) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid selling price.\n");
        } else
        {
            break;
        }
    }

    strcpy(property.registrationDate, registrationDate);
    property.isActive = 1;
    strcpy(property.registeredBy, currentUser->username);

    FILE *file = fopen("commercial_properties.txt", "a");
    if (file != NULL)
    {
        fprintf(file, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%.2lf,%s\n",
                property.propertyId,
                property.isActive,
                property.registeredBy,
                property.municipalityDistrict,
                property.address,
                property.propertyType,
                property.buildingAge,
                property.areaSize,
                property.floor,
                property.landArea,
                property.ownerPhoneNumber,
                property.officeRooms,
                property.sellingPrice,
                property.registrationDate);
        fclose(file);
        printf("Commercial property information saved successfully.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    }
    else
    {
        printf("Unable to save property information to file.\n");
        printf("Press any key to continue.\n");
        getch();
        fflush(stdin);
        system("cls");
        addInformation(currentUser);
    }
}

void registerLandSale(struct User* currentUser) {
    struct LandProperty land;
    char userInput[50];
    char phoneNumber[20];
    char registrationDate[11];

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(registrationDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

    int propertyCount = getPropertyCount();
    land.propertyId = propertyCount + 1;

    updatePropertyCount(land.propertyId);

    while (1)
    {
        printf("Enter municipality district number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            land.municipalityDistrict = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter exact address (Use a dash to separate): ");
        scanf(" %[^\n]s", land.address);
        if (!checkAddressFormat(land.address))
        {
            printf("The format is invalid. Please enter a valid address.\n");
        } else
        {
            break;
        }
    }
    printf("Enter land type (Agricultural or Urban): ");
    scanf(" %[^\n]s", land.landType);
    while (1)
    {
        printf("Enter land area (in square meters): ");
        if (scanf("%f", &land.landArea) != 1) {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid land area.\n");
        } else {
            break;
        }
    }
    while (1)
    {
        printf("Enter distance to main road: ");
        if (scanf("%f", &land.distanceToMainRoad) != 1) {
            while (getchar() != '\n');
            printf("The format is invalid.\n");
        } else {
            break;
        }
    }
    while (1)
    {
        printf("Does it have a well? (1 for Yes, 0 for No): ");
        scanf("%s", userInput);

        if (isNumber(userInput) && (strcmp(userInput , "1") == 0 || strcmp(userInput , "0") == 0) )
        {
            land.hasWell = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number (1 for Yes, 0 for No).\n");
        }
    }
    do {
        printf("Enter owner's phone number (09xxxxxxxxx): ");
        scanf(" %s", phoneNumber);
        if (!isValidPhoneNumber(phoneNumber)) {
            printf("Invalid phone number format. Please enter a valid Iranian mobile number starting with 09.\n");
        }
    } while (!isValidPhoneNumber(phoneNumber));
    strcpy(land.ownerPhoneNumber, phoneNumber);

    while (1)
    {
        printf("Enter selling price: ");
        if (scanf("%lf", &land.sellingPrice) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid selling price.\n");
        } else
        {
            break;
        }
    }

    strcpy(land.registrationDate, registrationDate);
    land.isActive = 1;
    strcpy(land.registeredBy, currentUser->username);

    FILE *file = fopen("land_properties.txt", "a");
    if (file != NULL) {
        fprintf(file, "%d,%d,%s,%d,%s,%s,%.2f,%.2f,%d,%s,%.2lf,%s\n",
                land.propertyId,
                land.isActive,
                land.registeredBy,
                land.municipalityDistrict,
                land.address,
                land.landType,
                land.landArea,
                land.distanceToMainRoad,
                land.hasWell,
                land.ownerPhoneNumber,
                land.sellingPrice,
                land.registrationDate);
        fclose(file);
        printf("Land property information saved successfully.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    } else {
        printf("Unable to save property information to file.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    }
}

void registerResidentialPropertyRental(struct User* currentUser)
{
    struct ResidentialProperty property;
    char userInput[50];
    char phoneNumber[20];
    char registrationDate[11];

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(registrationDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

    int propertyCount = getPropertyCount();
    property.propertyId = propertyCount + 1;

    updatePropertyCount(property.propertyId);

    // گرفتن اطلاعات ملک از کاربر
    while (1)
    {
        printf("Enter municipality district number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.municipalityDistrict = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter exact address (Use a dash to separate): ");
        scanf(" %[^\n]s", property.address);
        if (!checkAddressFormat(property.address))
        {
            printf("The format is invalid. Please enter a valid address.\n");
        } else
        {
            break;
        }
    }
    int choice;
    bool continueLoop = true;
    while (continueLoop)
    {
        printf("Enter property type (1.Apartment , 2.Villa  . 3.other): ");
        scanf("%s", userInput);
        if (!isNumber(userInput)) {
            printf("Invalid input! Please enter a number.\n");
        }
        else
        {
            choice = atoi(userInput);
            switch (choice)
            {
                case 1:
                    strcpy(property.propertyType, "Apartment");
                    continueLoop = false;
                    break;
                case 2:
                    strcpy(property.propertyType, "Villa");
                    continueLoop = false;
                    break;
                case 3:
                    printf("Please enter the property type: ");
                    scanf(" %[^\n]s", property.propertyType);
                    continueLoop = false;
                    break;
                default:
                    printf("Invalid choice, please try again.\n");
                    break;
            }
        }
    }
    while (1)
    {
        printf("Enter building age: ");
        scanf("%s", userInput);

        if (isNumber(userInput)) {
            property.buildingAge = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }

    while (1)
    {
        printf("Enter area size (in square meters): ");
        if (scanf("%f", &property.areaSize) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid . Please enter a valid area size.\n");
        } else {
            break;
        }
    }

    while (1)
    {
        printf("Enter land area (in square meters): ");
        if (scanf("%f", &property.landArea) != 1 || property.landArea < property.areaSize) {
            while (getchar() != '\n');
            printf("The format is invalid or land area is less than area size. Please enter a valid land area.\n");
        } else {
            break;
        }
    }

    while (1)
    {
        printf("Enter floor number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.floor = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }

    do {
        printf("Enter owner's phone number (09xxxxxxxxx): ");
        scanf(" %s", phoneNumber);
        if (!isValidPhoneNumber(phoneNumber)) {
            printf("Invalid phone number format. Please enter a valid Iranian mobile number starting with 09.\n");
        }
    } while (!isValidPhoneNumber(phoneNumber));
    strcpy(property.ownerPhoneNumber, phoneNumber);

    while (1)
    {
        printf("Enter number of bedrooms: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.bedrooms = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }

    }
    while (1)
    {
        printf("Enter mortgage amount: ");
        if (scanf("%lf", &property.mortgageAmount) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid mortgage amount.\n");
        } else
        {
            break;
        }
    }
    while (1)
    {
        printf("Enter monthly rent amount: ");
        if (scanf("%lf", &property.monthlyRentAmount) != 1 || property.mortgageAmount < property.monthlyRentAmount)
        {
            while (getchar() != '\n');
            printf("The format is invalid or monthly rent amount is more than mortgage amount. Please enter a valid monthly rent amount.\n");
        } else
        {
            break;
        }
    }

    strcpy(property.registrationDate, registrationDate);
    property.isActive = 1;
    strcpy(property.registeredBy, currentUser->username);

    FILE *file = fopen("residential_properties_rental.txt", "a");
    if (file != NULL)
    {
        fprintf(file, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%.2lf,%.2lf,%s\n",
                property.propertyId,
                property.isActive,
                property.registeredBy,
                property.municipalityDistrict,
                property.address,
                property.propertyType,
                property.buildingAge,
                property.areaSize,
                property.floor,
                property.landArea,
                property.ownerPhoneNumber,
                property.bedrooms,
                property.mortgageAmount,
                property.monthlyRentAmount,
                property.registrationDate);

        fclose(file);
        printf("\nResidential property information saved successfully.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    }
    else
    {
        printf("\nUnable to save property information to file.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    }
}

void registerCommercialPropertyRental(struct User* currentUser)
{
    struct CommercialProperty property;
    char userInput[50];
    char phoneNumber[20];
    char registrationDate[11];

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(registrationDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

    int propertyCount = getPropertyCount();
    property.propertyId = propertyCount + 1;
    updatePropertyCount(property.propertyId);

    while (1)
    {
        printf("Enter municipality district number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.municipalityDistrict = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter exact address (Use a dash to separate): ");
        scanf(" %[^\n]s", property.address);
        if (!checkAddressFormat(property.address))
        {
            printf("The format is invalid. Please enter a valid address.\n");
        } else
        {
            break;
        }
    }
    printf("Enter property type (Office, Administrative location, etc.): ");
    scanf(" %[^\n]s", property.propertyType);
    while (1)
    {
        printf("Enter building age: ");
        scanf("%s", userInput);

        if (isNumber(userInput)) {
            property.buildingAge = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }

    while (1)
    {
        printf("Enter area size (in square meters): ");
        if (scanf("%f", &property.areaSize) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid . Please enter a valid area size.\n");
        } else {
            break;
        }
    }

    while (1)
    {
        printf("Enter land area (in square meters): ");
        if (scanf("%f", &property.landArea) != 1 || property.landArea < property.areaSize)
        {
            while (getchar() != '\n');
            printf("The format is invalid or land area is less than area size. Please enter a valid land area.\n");
        } else {
            break;
        }
    }

    while (1)
    {
        printf("Enter floor number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.floor = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    do {
        printf("Enter owner's phone number (09xxxxxxxxx): ");
        scanf(" %s", phoneNumber);
        if (!isValidPhoneNumber(phoneNumber)) {
            printf("Invalid phone number format. Please enter a valid Iranian mobile number starting with 09.\n");
        }
    } while (!isValidPhoneNumber(phoneNumber));
    strcpy(property.ownerPhoneNumber, phoneNumber);
    while (1)
    {
        printf("Enter number of office rooms: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            property.officeRooms = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }

    }
    while (1)
    {
        printf("Enter mortgage amount: ");
        if (scanf("%lf", &property.mortgageAmount) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid mortgage amount.\n");
        } else
        {
            break;
        }
    }
    while (1)
    {
        printf("Enter monthly rent amount: ");
        if (scanf("%lf", &property.monthlyRentalAmount) != 1 || property.mortgageAmount < property.monthlyRentalAmount)
        {
            while (getchar() != '\n');
            printf("The format is invalid or monthly rent amount is more than mortgage amount. Please enter a valid monthly rent amount.\n");
        } else
        {
            break;
        }
    }


    strcpy(property.registrationDate, registrationDate);
    property.isActive = 1;
    strcpy(property.registeredBy, currentUser->username);

    FILE *file = fopen("commercial_properties_rental.txt", "a");
    if (file != NULL)
    {
        fprintf(file, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%.2lf,%.2lf,%s\n",
                property.propertyId,
                property.isActive,
                property.registeredBy,
                property.municipalityDistrict,
                property.address,
                property.propertyType,
                property.buildingAge,
                property.areaSize,
                property.floor,
                property.landArea,
                property.ownerPhoneNumber,
                property.officeRooms,
                property.monthlyRentalAmount,
                property.mortgageAmount,
                property.registrationDate);
        fclose(file);
        printf("\nCommercial property rental information saved successfully.\n");
        printf("Press any key to continue.\n");
        getch();
        fflush(stdin);
        system("cls");
        addInformation(currentUser);
    }
    else
    {
        printf("\nUnable to save property rental information to file.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    }
}

void registerLandRental(struct User* currentUser)
{
    struct LandProperty land;
    char userInput[50];
    char phoneNumber[20];
    char registrationDate[11];

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    sprintf(registrationDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

    int propertyCount = getPropertyCount();
    land.propertyId = propertyCount + 1;

    updatePropertyCount(land.propertyId);

    while (1)
    {
        printf("Enter municipality district number: ");
        scanf("%s", userInput);

        if (isNumber(userInput))
        {
            land.municipalityDistrict = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number.\n");
        }
    }
    while (1)
    {
        printf("Enter exact address (Use a dash to separate): ");
        scanf(" %[^\n]s", land.address);
        if (!checkAddressFormat(land.address))
        {
            printf("The format is invalid. Please enter a valid address.\n");
        } else
        {
            break;
        }
    }
    printf("Enter land type (Agricultural or Urban): ");
    scanf(" %[^\n]s", land.landType);
    while (1)
    {
        printf("Enter land area (in square meters): ");
        if (scanf("%f", &land.landArea) != 1) {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid land area.\n");
        } else {
            break;
        }
    }
    while (1)
    {
        printf("Enter distance to main road: ");
        if (scanf("%f", &land.distanceToMainRoad) != 1) {
            while (getchar() != '\n');
            printf("The format is invalid.\n");
        } else {
            break;
        }
    }
    while (1)
    {
        printf("Does it have a well? (1 for Yes, 0 for No): ");
        scanf("%s", userInput);

        if (isNumber(userInput) && (strcmp(userInput , "1") == 0 || strcmp(userInput , "0") == 0) )
        {
            land.hasWell = atoi(userInput);
            break;
        } else {
            printf("Invalid input! Please enter a number (1 for Yes, 0 for No).\n");
        }
    }
    do {
        printf("Enter owner's phone number (09xxxxxxxxx): ");
        scanf(" %s", phoneNumber);
        if (!isValidPhoneNumber(phoneNumber)) {
            printf("Invalid phone number format. Please enter a valid Iranian mobile number starting with 09.\n");
        }
    } while (!isValidPhoneNumber(phoneNumber));
    strcpy(land.ownerPhoneNumber, phoneNumber);
    while (1)
    {
        printf("Enter mortgage amount: ");
        if (scanf("%lf", &land.mortgageAmount) != 1)
        {
            while (getchar() != '\n');
            printf("The format is invalid. Please enter a valid mortgage amount.\n");
        } else
        {
            break;
        }
    }
    while (1)
    {
        printf("Enter monthly rent amount: ");
        if (scanf("%lf", &land.monthlyRentAmount) != 1 || land.mortgageAmount < land.monthlyRentAmount)
        {
            while (getchar() != '\n');
            printf("The format is invalid or monthly rent amount is more than mortgage amount. Please enter a valid monthly rent amount.\n");
        } else
        {
            break;
        }
    }

    strcpy(land.registrationDate, registrationDate);
    land.isActive = 1;
    strcpy(land.registeredBy, currentUser->username);

    FILE *file = fopen("land_properties_rental.txt", "a");
    if (file != NULL) {
        fprintf(file, "%d,%d,%s,%d,%s,%s,%.2f,%.2f,%d,%s,%.2lf,%.2lf,%s\n",
                land.propertyId,
                land.isActive,
                land.registeredBy,
                land.municipalityDistrict,
                land.address,
                land.landType,
                land.landArea,
                land.distanceToMainRoad,
                land.hasWell,
                land.ownerPhoneNumber,
                land.mortgageAmount,
                land.monthlyRentAmount,
                land.registrationDate);
        fclose(file);
        printf("\nLand property information saved successfully.\n");
        printf("Press any key to continue.\n");
        getch();
        system("cls");
        addInformation(currentUser);
    } else {
        printf("\nUnable to save property information to file.\n");
        printf("Press any key to continue.\n");
        getch();
        fflush(stdin);
        system("cls");
        addInformation(currentUser);
    }
}

//توابع آرشیو اطلاعات

void deleteResidential(struct User* currentUser)
{

    FILE *file = fopen("residential_properties.txt", "r+");
    if (file != NULL)
    {
        printf("Properties registered by you:\n");
        printf("\nPropertyId - Registered by - registration date- Address -  - ... (other fields)\n\n");

        char line[256];
        int propertyIdToDeactivate; // آی دی ملک برای غیرفعال کردن
        int found = 0;

        while (fgets(line, sizeof(line), file))
        {
            struct ResidentialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.bedrooms,
                &property.sellingPrice, property.registrationDate);

            if (strcmp(property.registeredBy, currentUser) == 0 && property.isActive == 1) {
                printf("%d - %s - %s - %s - ... (other fields)\n", property.propertyId, property.registeredBy, property.registrationDate, property.address );
            }
        }

        char option; // انتخاب یا عدم انتخاب کاربر جهت ادامه یا بازگشت
        printf("\n!!Do you want to go back to the previous menu or continue?\n (Enter 'y' to continue, Enter 'n' to return) : ");
        while (1)
        {
            option = getche();
            if (option != 'y' && option != 'n')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'y' for continue, 'n' for return: ");
            }
            else
            {
                printf("\n\n");
                break;
            }
        }
        if (option == 'n') {
            system("cls");
            fclose(file);
            archive(currentUser);
        }

        time_t t = time(NULL); // گرفتن زمان فعلی
        struct tm tm = *localtime(&t); // تبدیل زمان به ساختار تاریخ/زمان محلی
        char deleteDate[11]; // تعریف یک رشته برای ذخیره تاریخ حذف
        sprintf(deleteDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday); // تبدیل مقادیر ساعت محلی به رشته تاریخ حذف

        printf("Enter the propertyId to deactivate: ");
        scanf("%d", &propertyIdToDeactivate);

        rewind(file); // بازنویسی پوینتر فایل به ابتدا
        FILE *tempFile = fopen("temp.txt", "w"); // باز کردن فایل موقت برای نوشتن
        while (fgets(line, sizeof(line), file)) { // حلقه خواندن اطلاعات از فایل
            struct ResidentialProperty property; // تعریف یک ساختار برای ذخیره مشخصات ملک
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.bedrooms,
                &property.sellingPrice, property.registrationDate); // خواندن اطلاعات هر خط از فایل

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0) { // بررسی اینکه آیا کاربر فعلی اجازه غیرفعال کردن ملک را دارد یا نه
                property.isActive = 0;
                found = 1;
                strcpy(property.deleteDate, deleteDate); // تنظیم تاریخ حذف برای ملک
            }
            fprintf(tempFile, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%lf,%s",
                property.propertyId, property.isActive, property.registeredBy,
                property.municipalityDistrict, property.address, property.propertyType,
                property.buildingAge, property.areaSize, property.floor,
                property.landArea, property.ownerPhoneNumber, property.bedrooms,
                property.sellingPrice, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0) { // بررسی مجدد برای نوشتن تاریخ حذف ملک
                fprintf(tempFile, ",%s\n", property.deleteDate);
            }
            else
            {
                fprintf(tempFile, "\n"); // جدا کردن خطوط
            }
        }
        fclose(file);
        fclose(tempFile);

        remove("residential_properties.txt");
        rename("temp.txt", "residential_properties.txt");

        if (found)
        {
            system("cls");
            printf("Property with ID %d deactivated successfully.\n", propertyIdToDeactivate);
            Beep(500, 60); // پخش صدا
            Beep(1000, 60);
            printf("Press any key to continue.\n");
            getch();
            system("cls");
            archive(currentUser);
        }
        else
        {
            system("cls");
            printf("Property not found or you don't have permission to deactivate it.\n");
            archive(currentUser);
        }
        } else {
            printf("Unable to open property file.\n");
            usleep(1000000);
            archive(currentUser);
        }
}

void deleteCommercial(struct User* currentUser)
{
    FILE *file = fopen("commercial_properties.txt", "r+");
    if (file != NULL)
    {
        printf("Properties registered by you:\n");
        printf("\nPropertyId - Registered by - registration date- Address -  - ... (other fields)\n\n");

        char line[256];
        int propertyIdToDeactivate;
        int found = 0;

        while (fgets(line, sizeof(line), file))
        {
            struct CommercialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.officeRooms,
                &property.sellingPrice, property.registrationDate);

            if (strcmp(property.registeredBy, currentUser) == 0 && property.isActive == 1) {
                printf("%d - %s - %s - %s - ... (other fields)\n", property.propertyId, property.registeredBy, property.registrationDate, property.address );
            }
        }

        char option;
        printf("\n!!Do you want to go back to the previous menu or continue?\n (Enter 'y' to continue, Enter 'n' to return) : ");
        while (1)
        {
            option = getche();
            if (option != 'y' && option != 'n')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'y' for continue, 'n' for return: ");
            }
            else
            {
                printf("\n\n");
                break;
            }
        }
        if (option == 'n') {
            system("cls");
            fclose(file);
            archive(currentUser);
        }


        time_t t = time(NULL);
        struct tm tm = *localtime(&t);
        char deleteDate[11];
        sprintf(deleteDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

        printf("Enter the propertyId to deactivate: ");
        scanf("%d", &propertyIdToDeactivate);

        // Move file pointer to the beginning
        rewind(file);
        FILE *tempFile = fopen("temp.txt", "w");

        while (fgets(line, sizeof(line), file))
        {
            struct CommercialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.officeRooms,
                &property.sellingPrice, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0) {
                property.isActive = 0;  // Deactivate the property
                found = 1;
                strcpy(property.deleteDate, deleteDate);
            }
            fprintf(tempFile, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%lf,%s",
                property.propertyId, property.isActive, property.registeredBy,
                property.municipalityDistrict, property.address, property.propertyType,
                property.buildingAge, property.areaSize, property.floor,
                property.landArea, property.ownerPhoneNumber, property.officeRooms,
                property.sellingPrice, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0)
            {
                fprintf(tempFile, ",%s\n", property.deleteDate);
            }
            else
            {
                fprintf(tempFile, "\n");
            }
        }

        fclose(file);
        fclose(tempFile);

        remove("commercial_properties.txt");
        rename("temp.txt", "commercial_properties.txt");

        if (found) {
            system("cls");
            printf("Property with ID %d deactivated successfully.\n", propertyIdToDeactivate);
            Beep(500, 60);
            Beep(1000, 60);
            printf("Press any key to continue.\n");
            getch();
            system("cls");
            archive(currentUser);
        } else {
            system("cls");
            printf("Property not found or you don't have permission to deactivate it.\n");
            archive(currentUser);
        }
    }
    else
    {
        printf("Unable to open property file.\n");
        usleep(1000000);
        archive(currentUser);
    }
}


void deleteLand(struct User* currentUser)
{
    FILE *file = fopen("land_properties.txt", "r+");
    if (file != NULL)
    {
        printf("Properties registered by you:\n");
        printf("\nPropertyId - Registered by - registration date- Address -  - ... (other fields)\n\n");

        char line[256];
        int propertyIdToDeactivate;
        int found = 0;

        while (fgets(line, sizeof(line), file))
        {
            struct LandProperty land;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%s",
                &land.propertyId, &land.isActive, land.registeredBy,
                &land.municipalityDistrict, land.address, land.landType,
                &land.landArea, &land.distanceToMainRoad, &land.hasWell,
                land.ownerPhoneNumber, &land.sellingPrice, land.registrationDate);

            if (strcmp(land.registeredBy, currentUser) == 0 && land.isActive == 1) {
                printf("%d - %s - %s - %s - ... (other fields)\n", land.propertyId, land.registeredBy, land.registrationDate, land.address );
            }
        }

        char option;
        printf("\n!!Do you want to go back to the previous menu or continue?\n (Enter 'y' to continue, Enter 'n' to return) : ");
        while (1)
        {
            option = getche();
            if (option != 'y' && option != 'n')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'y' for continue, 'n' for return: ");
            }
            else
            {
                printf("\n\n");
                break;
            }
        }
        if (option == 'n') {
            system("cls");
            fclose(file);
            archive(currentUser);
        }

        time_t t = time(NULL);
        struct tm tm = *localtime(&t);
        char deleteDate[11];
        sprintf(deleteDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

        printf("Enter the propertyId to deactivate: ");
        scanf("%d", &propertyIdToDeactivate);

        rewind(file);
        FILE *tempFile = fopen("temp.txt", "w");

        while (fgets(line, sizeof(line), file))
        {
            struct LandProperty land;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%s",
                &land.propertyId, &land.isActive, land.registeredBy,
                &land.municipalityDistrict, land.address, land.landType,
                &land.landArea, &land.distanceToMainRoad, &land.hasWell,
                land.ownerPhoneNumber, &land.sellingPrice, land.registrationDate);

            if (land.propertyId == propertyIdToDeactivate) {
            {
                if (strcmp(land.registeredBy, currentUser) == 0)
                {
                    land.isActive = 0;
                    found = 1;
                    strcpy(land.deleteDate, deleteDate);
                }
                else
                {
                    printf("You don't have permission to deactivate this property.\n");
                    fclose(file);
                    fclose(tempFile);
                    remove("temp.txt");
                    return;  // End the function early
                }
            }

            fprintf(tempFile, "%d,%d,%s,%d,%s,%s,%.2f,%.2f,%d,%s,%lf,%s",
                land.propertyId, land.isActive, land.registeredBy,
                land.municipalityDistrict, land.address, land.landType,
                land.landArea, land.distanceToMainRoad, land.hasWell,
                land.ownerPhoneNumber, land.sellingPrice, land.registrationDate);

            if (land.propertyId == propertyIdToDeactivate && strcmp(land.registeredBy, currentUser) == 0)
            {
                fprintf(tempFile, ",%s\n", land.deleteDate);
            }
            else
            {
                fprintf(tempFile, "\n");
            }
        }

        fclose(file);
        fclose(tempFile);

        remove("land_properties.txt");
        rename("temp.txt", "land_properties.txt");

        if (found) {
            system("cls");
            printf("Property with ID %d deactivated successfully.\n", propertyIdToDeactivate);
            Beep(500, 60);
            Beep(1000, 60);
            printf("Press any key to continue.\n");
            getch();
            system("cls");
            archive(currentUser);
        } else {
            system("cls");
            printf("Property not found.\n");
            archive(currentUser);
            }
        }
    }
    else
    {
        printf("Unable to open property file.\n");
        usleep(1000000);
        archive(currentUser);
    }
}


void deleteResidentialRental(struct User* currentUser)
{

    FILE *file = fopen("residential_properties_rental.txt", "r+");
    if (file != NULL)
    {
        printf("Properties registered by you:\n");
        printf("\nPropertyId - Registered by - registration date- Address -  - ... (other fields)\n\n");

        char line[256];
        int propertyIdToDeactivate;
        int found = 0;

        while (fgets(line, sizeof(line), file))
        {
            struct ResidentialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.bedrooms,
                &property.mortgageAmount, &property.monthlyRentAmount, property.registrationDate);

            if (strcmp(property.registeredBy, currentUser) == 0 && property.isActive == 1) {
                printf("%d - %s - %s - %s - ... (other fields)\n", property.propertyId, property.registeredBy, property.registrationDate, property.address );
            }
        }

        char option;
        printf("\n!!Do you want to go back to the previous menu or continue?\n (Enter 'y' to continue, Enter 'n' to return) : ");
        while (1)
        {
            option = getche();
            if (option != 'y' && option != 'n')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'y' for continue, 'n' for return: ");
            }
            else
            {
                printf("\n\n");
                break;
            }
        }
        if (option == 'n') {
            system("cls");
            fclose(file);
            archive(currentUser);
        }

        time_t t = time(NULL);
        struct tm tm = *localtime(&t);
        char deleteDate[11];
        sprintf(deleteDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

        printf("Enter the propertyId to deactivate: ");
        scanf("%d", &propertyIdToDeactivate);

        rewind(file);
        FILE *tempFile = fopen("temp_rental.txt", "w");

        while (fgets(line, sizeof(line), file))
        {
            struct ResidentialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.bedrooms,
                &property.mortgageAmount, &property.monthlyRentAmount, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0)
            {
                property.isActive = 0;
                found = 1;
                strcpy(property.deleteDate, deleteDate);
            }

            fprintf(tempFile, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%lf,%lf,%s",
                property.propertyId, property.isActive, property.registeredBy,
                property.municipalityDistrict, property.address, property.propertyType,
                property.buildingAge, property.areaSize, property.floor,
                property.landArea, property.ownerPhoneNumber, property.bedrooms,
                property.mortgageAmount, property.monthlyRentAmount, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0)
            {
                fprintf(tempFile, ",%s\n", property.deleteDate);
            }
            else
            {
                fprintf(tempFile, "\n");
            }
        }

        fclose(file);
        fclose(tempFile);

        remove("residential_properties_rental.txt");
        rename("temp_rental.txt", "residential_properties_rental.txt");

        if (found) {
            system("cls");
            printf("Property with ID %d deactivated successfully.\n", propertyIdToDeactivate);
            Beep(500, 60);
            Beep(1000, 60);
            printf("Press any key to continue.\n");
            getch();
            system("cls");
            archive(currentUser);
        } else {
            system("cls");
            printf("Property not found or you don't have permission to deactivate it.\n");
            archive(currentUser);
        }
    }
    else
    {
        printf("Unable to open property file.\n");
        usleep(1000000);
        archive(currentUser);
    }
}

void deleteCommercialRental(struct User* currentUser)
{
    FILE *file = fopen("commercial_properties_rental.txt", "r+");
    if (file != NULL)
    {
        printf("Properties registered by you:\n");
        printf("\nPropertyId - Registered by - registration date- Address -  - ... (other fields)\n\n");

        char line[256];
        int propertyIdToDeactivate;
        int found = 0;

        while (fgets(line, sizeof(line), file))
        {
            struct CommercialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.officeRooms,
                &property.monthlyRentalAmount, &property.mortgageAmount, property.registrationDate);

            if (strcmp(property.registeredBy, currentUser) == 0 && property.isActive == 1) {
                printf("%d - %s - %s - %s - ... (other fields)\n", property.propertyId, property.registeredBy, property.registrationDate, property.address );
            }
        }
        char option;
        printf("\n!!Do you want to go back to the previous menu or continue?\n (Enter 'y' to continue, Enter 'n' to return) : ");
        while (1)
        {
            option = getche();
            if (option != 'y' && option != 'n')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'y' for continue, 'n' for return: ");
            }
            else
            {
                printf("\n\n");
                break;
            }
        }
        if (option == 'n')
        {
            system("cls");
            fclose(file);
            archive(currentUser);
        }

        time_t t = time(NULL);
        struct tm tm = *localtime(&t);
        char deleteDate[11];
        sprintf(deleteDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

        printf("Enter the propertyId to deactivate: ");
        scanf("%d", &propertyIdToDeactivate);

        rewind(file);
        FILE *tempFile = fopen("temp.txt", "w");

        while (fgets(line, sizeof(line), file))
        {
            struct CommercialProperty property;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                &property.propertyId, &property.isActive, property.registeredBy,
                &property.municipalityDistrict, property.address, property.propertyType,
                &property.buildingAge, &property.areaSize, &property.floor,
                &property.landArea, property.ownerPhoneNumber, &property.officeRooms,
                &property.monthlyRentalAmount, &property.mortgageAmount, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0) {
                property.isActive = 0;
                found = 1;
                strcpy(property.deleteDate, deleteDate);
            }

            fprintf(tempFile, "%d,%d,%s,%d,%s,%s,%d,%.2f,%d,%.2f,%s,%d,%lf,%lf,%s",
                property.propertyId, property.isActive, property.registeredBy,
                property.municipalityDistrict, property.address, property.propertyType,
                property.buildingAge, property.areaSize, property.floor,
                property.landArea, property.ownerPhoneNumber, property.officeRooms,
                property.monthlyRentalAmount, property.mortgageAmount, property.registrationDate);

            if (property.propertyId == propertyIdToDeactivate && strcmp(property.registeredBy, currentUser) == 0)
            {
                fprintf(tempFile, ",%s\n", property.deleteDate);
            }
            else
            {
                fprintf(tempFile, "\n");
            }
        }

        fclose(file);
        fclose(tempFile);

        remove("commercial_properties_rental.txt");
        rename("temp.txt", "commercial_properties_rental.txt");

        if (found) {
            system("cls");
            printf("Property with ID %d deactivated successfully.\n", propertyIdToDeactivate);
            Beep(500, 60);
            Beep(1000, 60);
            printf("Press any key to continue.\n");
            getch();
            system("cls");
            archive(currentUser);
        } else {
            system("cls");
            printf("Property not found or you don't have permission to deactivate it.\n");
            archive(currentUser);
        }
    }
    else
    {
        printf("Unable to open property file.\n");
        usleep(1000000);
        archive(currentUser);
    }
}


void deleteLandRental(struct User* currentUser)
{
    FILE *file = fopen("land_properties_rental.txt", "r+");
    if (file != NULL)
    {
        printf("Properties registered by you:\n");
        printf("\nPropertyId - Registered by - registration date- Address -  - ... (other fields)\n\n");

        char line[256];
        int propertyIdToDeactivate;
        int found = 0;

        while (fgets(line, sizeof(line), file))
        {
            struct LandProperty land;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%lf,%s\n",
                &land.propertyId, &land.isActive, land.registeredBy,
                &land.municipalityDistrict, land.address, land.landType,
                &land.landArea, &land.distanceToMainRoad,
                &land.hasWell, land.ownerPhoneNumber,
                &land.mortgageAmount, &land.monthlyRentAmount,
                land.registrationDate);

            if (strcmp(land.registeredBy, currentUser) == 0 && land.isActive == 1) {
                printf("%d - %s - %s - %s - ... (other fields)\n", land.propertyId, land.registeredBy, land.registrationDate, land.address);
            }
        }
        char option;
        printf("\n!!Do you want to go back to the previous menu or continue?\n (Enter 'y' to continue, Enter 'n' to return) : ");
        while (1)
        {
            option = getche();
            if (option != 'y' && option != 'n')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'y' for continue, 'n' for return: ");
            }
            else
            {
                printf("\n\n");
                break;
            }
        }
        if (option == 'n') {
            system("cls");
            fclose(file);
            archive(currentUser);
        }

        time_t t = time(NULL);
        struct tm tm = *localtime(&t);
        char deleteDate[11];
        sprintf(deleteDate, "%04d-%02d-%02d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

        printf("Enter the propertyId to deactivate: ");
        scanf("%d", &propertyIdToDeactivate);

        rewind(file);
        FILE *tempFile = fopen("temp.txt", "w");

        while (fgets(line, sizeof(line), file))
        {
            struct LandProperty land;
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%lf,%s\n",
                &land.propertyId, &land.isActive, land.registeredBy,
                &land.municipalityDistrict, land.address, land.landType,
                &land.landArea, &land.distanceToMainRoad,
                &land.hasWell, land.ownerPhoneNumber,
                &land.mortgageAmount, &land.monthlyRentAmount,
                land.registrationDate);

            if (land.propertyId == propertyIdToDeactivate && strcmp(land.registeredBy, currentUser) == 0) {
                land.isActive = 0;
                found = 1;
                strcpy(land.deleteDate, deleteDate);
            }

            fprintf(tempFile, "%d,%d,%s,%d,%s,%s,%.2f,%.2f,%d,%s,%lf,%lf,%s",
                land.propertyId, land.isActive, land.registeredBy,
                land.municipalityDistrict, land.address, land.landType,
                land.landArea, land.distanceToMainRoad, land.hasWell,
                land.ownerPhoneNumber, land.mortgageAmount, land.monthlyRentAmount,
                land.registrationDate);

            if (land.propertyId == propertyIdToDeactivate && strcmp(land.registeredBy, currentUser) == 0)
            {
                fprintf(tempFile, ",%s\n", land.deleteDate);
            }
            else
            {
                fprintf(tempFile, "\n");
            }
        }

        fclose(file);
        fclose(tempFile);

        remove("land_properties_rental.txt");
        rename("temp.txt", "land_properties_rental.txt");

        if (found) {
            system("cls");
            printf("Property with ID %d deactivated successfully.\n", propertyIdToDeactivate);
            Beep(500, 60);
            Beep(1000, 60);
            printf("Press any key to continue.\n");
            getch();
            system("cls");
            archive(currentUser);
        } else {
            system("cls");
            printf("Property not found or you don't have permission to deactivate it.\n");
            archive(currentUser);
        }
    }
    else
    {
        printf("Unable to open property file.\n");
        usleep(1000000);
        archive(currentUser);
    }
}

int countProperties(const char *filename) // تابع شمارش تعداد املاک ببرای تولید گزارش
{
    int count = 0;
    FILE *file = fopen(filename, "r");
    if (file != NULL)
    {
        char line[256];
        while (fgets(line, sizeof(line), file))
        {
            count++;
        }
        fclose(file);
    }
    else {
        perror("Error opening file");
        usleep(900000);
        exit(1);
    }
    return count;
}

void createBarChart(int count1, int count2, int count3, int count4, int count5, int count6)
{
    int total = count1 + count2 + count3 + count4 + count5 + count6; // مجموع تعداد های ورودی را محاسبه می‌کنیم
    // درصد و تعداد را چاپ می‌کنیم
    printf("Residential for sale:  ");
    for (int i = 0; i < (count1 * 100 / total); i++) {
        printf("%c", 219); // Use ASCII code for "█"
    }
    printf(" (%d%%): %d\n", (count1 * 100 / total) , count1);

    printf("Residential for rent:  ");
    for (int i = 0; i < (count2 * 100 / total); i++) {
        printf("%c", 219);
    }
    printf(" (%d%%): %d\n", (count2 * 100 / total) , count2);

    printf("Commercial for sale:   ");
    for (int i = 0; i < (count3 * 100 / total); i++) {
        printf("%c", 219);
    }
    printf(" (%d%%): %d\n", (count3 * 100 / total), count3);

    printf("Commercial for rent:   ");
    for (int i = 0; i < (count4 * 100 / total); i++) {
        printf("%c", 219);
    }
    printf(" (%d%%): %d\n", (count4 * 100 / total), count4);

    printf("Land for sale:         ");
    for (int i = 0; i < (count5 * 100 / total); i++) {
        printf("%c", 219);
    }
    printf(" (%d%%): %d\n", (count5 * 100 / total), count5);

    printf("Land for rent:         ");
    for (int i = 0; i < (count6 * 100 / total); i++) {
        printf("%c", 219);
    }
    printf(" (%d%%): %d\n", (count6 * 100 / total), count6);
}

 /* تعداد ورودی‌های مختلف را از فایل‌های مختلف بدست می‌آوریم و بعد از آن از تابع
  استفاده می‌کنیم تا نمودارها را ایجاد کنیم createBarChart*/
void showNumberOfProperties(struct User *currentUser)
{
    int residentialCount = countProperties("residential_properties.txt");
    int residentialRentalCount = countProperties("residential_properties_rental.txt");
    int commercialCount = countProperties("commercial_properties.txt");
    int commercialRentalCount = countProperties("commercial_properties_rental.txt");
    int landCount = countProperties("land_properties.txt");
    int landRentalCount = countProperties("land_properties_rental.txt");
    // ساخت نمودار با تعداد‌های محاسبه شده
    createBarChart(residentialCount, residentialRentalCount, commercialCount, commercialRentalCount, landCount, landRentalCount);

    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche(); // دریافت ورودی کاربر
        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls"); // refresh صفحه
            showNumberOfProperties(currentUser);
        }
        else if (input == 'b')
        {
            system("cls");
            generateReports(currentUser);
        }
    }
}

void listPropertiesByMunicipalArea(struct User* currentUser)
{
    // Open the file based on municipalityDistrict and property type
    FILE* file;
    char fileName[100];

    // Check property type
    char propertyType[20];
    int propertyNum;
    int municipalityDistrict;

    printf("Enter the municipalityDistrict: ");
    scanf("%d", &municipalityDistrict);
    printf("Enter the property type (1.residential, 2.commercial, 3.land , 4.residential rental, 5.commercial rental, 6.land rental ): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential");
        snprintf(fileName, sizeof(fileName), "residential_properties.txt");
        break;
    case 2:
        strcpy(propertyType, "commercial");
        snprintf(fileName, sizeof(fileName), "commercial_properties.txt");
        break;
    case 3:
        strcpy(propertyType, "land");
        snprintf(fileName, sizeof(fileName), "land_properties.txt");
        break;
    case 4:
        strcpy(propertyType, "residential rental");
        snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
        break;
    case 5:
        strcpy(propertyType, "commercial rental");
        snprintf(fileName, sizeof(fileName), "commercial_properties_rental.txt");
        break;
    case 6:
        strcpy(propertyType, "land rental");
        snprintf(fileName, sizeof(fileName), "land_properties_rental.txt");
        break;
    default:
        printf("Invalid property type!\n");
        usleep(900000);
        generateReports(currentUser);
    }

    // Open the file
    file = fopen(fileName, "r");
    if (file == NULL) {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(900000);
        generateReports(currentUser);
    }

    // Read properties from the file and filter by municipalityDistrict
    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file))
    {
        // Parse the line and extract relevant fields
        int currentDistrict;
        sscanf(line, "%*[^,],%d,%*[^,],%d", &isActive ,&currentDistrict);
        if (currentDistrict == municipalityDistrict && isActive == 1)
        {
            // Create and insert the property node
            if (strcmp(propertyType, "residential") == 0)
            {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "commercial") == 0)
            {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "land") == 0)
            {
            struct LandProperty* property = malloc(sizeof(struct LandProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%s",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->landType,
                &property->landArea, &property->distanceToMainRoad, &property->hasWell,
                property->ownerPhoneNumber, &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "residential rental") == 0)
            {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "commercial rental") == 0)
            {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "land rental") == 0)
            {
            struct LandProperty* property = malloc(sizeof(struct LandProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->landType,
                &property->landArea, &property->distanceToMainRoad,
                &property->hasWell, property->ownerPhoneNumber,
                &property->mortgageAmount, &property->monthlyRentAmount,
                property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
        }
    }
    fclose(file);

    // Display the filtered properties
    struct PropertyNode* current = propertyList;
    while (current != NULL) {
        // Cast the property based on property type
        if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Property Type: %s\n", property->propertyType);
            printf("Building Age: %d\n", property->buildingAge);
            printf("Area Size: %f\n", property->areaSize);
            printf("Floor: %d\n", property->floor);
            printf("Land Area: %f\n", property->landArea);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Bedrooms: %d\n", property->bedrooms);
            printf("Selling Price: %lf\n", property->sellingPrice);
        } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Property Type: %s\n", property->propertyType);
            printf("Building Age: %d\n", property->buildingAge);
            printf("Area Size: %f\n", property->areaSize);
            printf("Floor: %d\n", property->floor);
            printf("Land Area: %f\n", property->landArea);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Office Rooms: %d\n", property->officeRooms);
            printf("Selling Price: %lf\n", property->sellingPrice);
        } else if (strcmp(propertyType, "land") == 0) {
            struct LandProperty* property = (struct LandProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Land Type: %s\n", property->landType);
            printf("Land Area: %f\n", property->landArea);
            printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
            printf("Has Well: %d\n", property->hasWell);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Selling Price: %lf\n", property->sellingPrice);
        }
        else if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Property Type: %s\n", property->propertyType);
            printf("Building Age: %d\n", property->buildingAge);
            printf("Area Size: %f\n", property->areaSize);
            printf("Floor: %d\n", property->floor);
            printf("Land Area: %f\n", property->landArea);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Bedrooms: %d\n", property->bedrooms);
            printf("Mortgage Amount: %lf\n", property->mortgageAmount);
            printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
        }


        else if (strcmp(propertyType, "commercial rental") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Property Type: %s\n", property->propertyType);
            printf("Building Age: %d\n", property->buildingAge);
            printf("Area Size: %f\n", property->areaSize);
            printf("Floor: %d\n", property->floor);
            printf("Land Area: %f\n", property->landArea);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Office Rooms: %d\n", property->officeRooms);
            printf("Mortgage Amount: %lf\n", property->mortgageAmount);
            printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
        }
        else if (strcmp(propertyType, "land rental") == 0) {
            struct LandProperty* property = (struct LandProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Land Type: %s\n", property->landType);
            printf("Land Area: %f\n", property->landArea);
            printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
            printf("Has Well: %d\n", property->hasWell);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Mortgage Amount: %lf\n", property->mortgageAmount);
            printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
        }
        printf("------------------\n");
        current = current->next;
    }
    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls");
            listPropertiesByMunicipalArea(currentUser);
        }
        else if (input == 'b')
        {
            // Free the property list
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser); // بازگشت به منوی قبلی
        }
    }
}

void listPropertiesByAge(struct User* currentUser)
{
    FILE* file;
    char fileName[100];
    char propertyType[20];
    int propertyNum;

    int minAge, maxAge;
    printf("Enter the minimum building age: ");
    scanf("%d", &minAge);
    printf("Enter the maximum building age: ");
    scanf("%d", &maxAge);

    printf("Enter the property type (1.residential, 2.commercial, 3.residential rental, 4.commercial rental): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential");
        snprintf(fileName, sizeof(fileName), "residential_properties.txt");
        break;
    case 2:
        strcpy(propertyType, "commercial");
        snprintf(fileName, sizeof(fileName), "commercial_properties.txt");
        break;
    case 3:
        strcpy(propertyType, "residential rental");
        snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
        break;
    case 4:
        strcpy(propertyType, "commercial rental");
        snprintf(fileName, sizeof(fileName), "commercial_properties_rental.txt");
        break;
    default:
        printf("Invalid property type!\n");
        fflush(stdin);
        usleep(900000);
        generateReports(currentUser);
    }

    file = fopen(fileName, "r");
    if (file == NULL) {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(900000);
        generateReports(currentUser);
    }

    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file))
    {
        int currentDistrict;
        sscanf(line, "%*[^,],%d,%*[^,]%*[^,]", &isActive );
        if (isActive == 1) {
            if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
        } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
        }
            else if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
            }
            else if (strcmp(propertyType, "commercial rental") == 0) {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }

        }
    }

    fclose(file);

    // Display the filtered properties
    struct PropertyNode* current = propertyList;
    while (current != NULL) {
        if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            if (property->buildingAge >= minAge && property->buildingAge <= maxAge) {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Bedrooms: %d\n", property->bedrooms);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            if (property->buildingAge >= minAge && property->buildingAge <= maxAge)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Office Rooms: %d\n", property->officeRooms);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        }
        else if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            if (property->buildingAge >= minAge && property->buildingAge <= maxAge)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Bedrooms: %d\n", property->bedrooms);
                printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
            }
        }
        else if (strcmp(propertyType, "commercial rental") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            if (property->buildingAge >= minAge && property->buildingAge <= maxAge)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Office Rooms: %d\n", property->officeRooms);
                printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
            }
        }
        printf("------------------\n");
        current = current->next;
    }
    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls");
            listPropertiesByAge(currentUser);
        }
        else if (input == 'b')
        {
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser);
        }
    }
}


void listPropertiesByAreaSize(struct User* currentUser)
{
    FILE* file;
    char fileName[100];
    char propertyType[20];
    int propertyNum;

    int minArea, maxArea;
    printf("Enter the minimum building area size: ");
    scanf("%d", &minArea);
    printf("Enter the maximum building area size: ");
    scanf("%d", &maxArea);

    printf("Enter the property type (1.residential, 2.commercial, 3.residential rental, 4.commercial rental): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential");
        snprintf(fileName, sizeof(fileName), "residential_properties.txt");
        break;
    case 2:
        strcpy(propertyType, "commercial");
        snprintf(fileName, sizeof(fileName), "commercial_properties.txt");
        break;
    case 3:
        strcpy(propertyType, "residential rental");
        snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
        break;
    case 4:
        strcpy(propertyType, "commercial rental");
        snprintf(fileName, sizeof(fileName), "commercial_properties_rental.txt");
        break;
    default:
        printf("Invalid property type!\n");
        fflush(stdin);
        usleep(900000);
        generateReports(currentUser);
    }

    file = fopen(fileName, "r");
    if (file == NULL) {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(900000);
        generateReports(currentUser);
    }

    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file))
    {
        int currentDistrict;
        sscanf(line, "%*[^,],%d,%*[^,]%*[^,]", &isActive );
        if (isActive == 1) {
            if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
        } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
        }
            else if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
            }
            else if (strcmp(propertyType, "commercial rental") == 0) {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }

        }
    }
    fclose(file);

    struct PropertyNode* current = propertyList;
    while (current != NULL) {
        if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            if (property->areaSize >= minArea && property->areaSize <= maxArea) {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Bedrooms: %d\n", property->bedrooms);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            if (property->areaSize >= minArea && property->areaSize <= maxArea)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Office Rooms: %d\n", property->officeRooms);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        }
        else if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            if (property->areaSize >= minArea && property->areaSize <= maxArea)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Bedrooms: %d\n", property->bedrooms);
                printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
            }
        }
        else if (strcmp(propertyType, "commercial rental") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            if (property->areaSize >= minArea && property->areaSize <= maxArea)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Office Rooms: %d\n", property->officeRooms);
                printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
            }
        }
        printf("------------------\n");
        current = current->next;
    }
    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls");
            listPropertiesByAge(currentUser);
        }
        else if (input == 'b')
        {
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser);
        }
    }
}

void listPropertiesByPrice(struct User* currentUser)
{

    FILE* file;
    char fileName[100];
    char propertyType[20];
    int propertyNum;

    int minPrice, maxPrice;
    printf("Enter the minimum building price: ");
    scanf("%d", &minPrice);
    printf("Enter the maximum building price: ");
    scanf("%d", &maxPrice);

    printf("\nEnter the property type (1.residential, 2.commercial, 3.land): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential");
        snprintf(fileName, sizeof(fileName), "residential_properties.txt");
        break;
    case 2:
        strcpy(propertyType, "commercial");
        snprintf(fileName, sizeof(fileName), "commercial_properties.txt");
        break;
    case 3:
        strcpy(propertyType, "land");
        snprintf(fileName, sizeof(fileName), "land_properties.txt");
        break;
    default:
        printf("Invalid property type!\n");
        fflush(stdin);
        usleep(300000);
        generateReports(currentUser);
    }

    file = fopen(fileName, "r");
    if (file == NULL) {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(300000);
        generateReports(currentUser);
    }
    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file)) {
        // Parse the line and extract relevant fields
        int currentDistrict;
        sscanf(line, "%*[^,],%d,%*[^,]%*[^,]", &isActive );
        if (isActive == 1)
        {
            if (strcmp(propertyType, "residential") == 0)
            {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "land") == 0) {
            struct LandProperty* property = malloc(sizeof(struct LandProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%s",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->landType,
                &property->landArea, &property->distanceToMainRoad, &property->hasWell,
                property->ownerPhoneNumber, &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
        }
    }
    fclose(file);

    struct PropertyNode* current = propertyList;
    while (current != NULL)
    {
        if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            if (property->sellingPrice >= minPrice && property->sellingPrice <= maxPrice)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Bedrooms: %d\n", property->bedrooms);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        } else if (strcmp(propertyType, "commercial") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            if (property->sellingPrice >= minPrice && property->sellingPrice <= maxPrice)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Office Rooms: %d\n", property->officeRooms);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        }
        else if (strcmp(propertyType, "land") == 0) {
            struct LandProperty* property = (struct LandProperty*)current->property;
            if (property->sellingPrice >= minPrice && property->sellingPrice <= maxPrice)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Land Type: %s\n", property->landType);
                printf("Land Area: %f\n", property->landArea);
                printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                printf("Has Well: %d\n", property->hasWell);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Selling Price: %lf\n", property->sellingPrice);
            }
        }
        printf("------------------\n");
        current = current->next;
    }
    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls");
            listPropertiesByPrice(currentUser);
        }
        else if (input == 'b')
        {
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser);
        }
    }
}


void listResidentialPropertiesByBedrooms(struct User* currentUser)
{
    FILE* file;
    char fileName[100];
    char propertyType[20];
    int propertyNum;
    int bedrooms;

    printf("Enter the number of bedrooms : ");
    scanf("%d", &bedrooms);

    printf("Enter the property type (1.residential, 2.residential rental): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential");
        snprintf(fileName, sizeof(fileName), "residential_properties.txt");
        break;
    case 2:
        strcpy(propertyType, "residential rental");
        snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
        break;
    default:
        printf("Invalid property type!\n");
        usleep(300000);
        generateReports(currentUser);
    }

    file = fopen(fileName, "r");
    if (file == NULL)
    {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(300000);
        generateReports(currentUser);
    }

    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file))
    {
        // Parse the line and extract relevant fields
        int currentBedrooms;
        sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%d", &isActive ,&currentBedrooms);
        if (currentBedrooms == bedrooms && isActive == 1)
        {
            // Create and insert the property node
            if (strcmp(propertyType, "residential") == 0)
            {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            } else if (strcmp(propertyType, "residential rental") == 0){
                struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
            }
        }
    }
    fclose(file);

    struct PropertyNode* current = propertyList;
    while (current != NULL)
        {
        if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Property Type: %s\n", property->propertyType);
            printf("Building Age: %d\n", property->buildingAge);
            printf("Area Size: %f\n", property->areaSize);
            printf("Floor: %d\n", property->floor);
            printf("Land Area: %f\n", property->landArea);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Bedrooms: %d\n", property->bedrooms);
            printf("Selling Price: %lf\n", property->sellingPrice);
        }
        else if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            printf("\nProperty ID: %d\n", property->propertyId);
            printf("Municipality District: %d\n", property->municipalityDistrict);
            printf("Address: %s\n", property->address);
            printf("Property Type: %s\n", property->propertyType);
            printf("Building Age: %d\n", property->buildingAge);
            printf("Area Size: %f\n", property->areaSize);
            printf("Floor: %d\n", property->floor);
            printf("Land Area: %f\n", property->landArea);
            printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
            printf("Bedrooms: %d\n", property->bedrooms);
            printf("Mortgage Amount: %lf\n", property->mortgageAmount);
            printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
        }
        printf("------------------\n");
        current = current->next;
    }
    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls");
            listResidentialPropertiesByBedrooms(currentUser);
        }
        else if (input == 'b')
        {
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser);
        }
    }
}

// تابع برای خواندن اطلاعات املاک از فایل مربوطه
void loadPropertiesFromFile(const char* filename, struct PropertyNode** propertyList)
{
    FILE* file = fopen(filename, "r");
    if (file != NULL) {
        char line[256];
        while (fgets(line, sizeof(line), file)) {
            if (strcmp(filename, "residential_properties.txt") == 0) {
                struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->sellingPrice, property->registrationDate);
                insertPropertyNode(propertyList, property);
            }
            else if (strcmp(filename, "commercial_properties.txt") == 0) {
                struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->sellingPrice, property->registrationDate);
                insertPropertyNode(propertyList, property);
            }
            else if (strcmp(filename, "land_properties.txt") == 0) {
                struct LandProperty* property = malloc(sizeof(struct LandProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%s",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->landType,
                    &property->landArea, &property->distanceToMainRoad, &property->hasWell,
                    property->ownerPhoneNumber, &property->sellingPrice, property->registrationDate);
                insertPropertyNode(propertyList, property);
            }
        }
        fclose(file);
    }
    else {
        printf("Error opening file %s\n", filename);
        usleep(300000);
        exit(1);
    }
}

// تابع برای محاسبه ارزش کل املاک ثبت شده در سیستم برای فروش
void calculateTotalPropertyValue(struct User* currentUser)
{
    double totalValue = 0.0;

    struct PropertyNode* residentialProperties = NULL;
    loadPropertiesFromFile("residential_properties.txt", &residentialProperties);
    struct PropertyNode* currentResidential = residentialProperties;
    while (currentResidential != NULL) {
        struct ResidentialProperty* property = (struct ResidentialProperty*)currentResidential->property;
        totalValue += property->sellingPrice;
        currentResidential = currentResidential->next;
    }
    freePropertyList(residentialProperties);

    struct PropertyNode* CommercialProperty = NULL;
    loadPropertiesFromFile("commercial_properties.txt", &CommercialProperty);
    struct PropertyNode* currentCommercial = CommercialProperty;
    while (currentCommercial != NULL) {
        struct CommercialProperty* property = (struct CommercialProperty*)currentCommercial->property;
        totalValue += property->sellingPrice;
        currentCommercial = currentCommercial->next;
    }
    freePropertyList(CommercialProperty);

    struct PropertyNode* LandProperty = NULL;
    loadPropertiesFromFile("land_properties.txt", &LandProperty);
    struct PropertyNode* currentLand = LandProperty;
    while (currentLand != NULL) {
        struct LandProperty* property = (struct LandProperty*)currentLand->property;
        totalValue += property->sellingPrice;
        currentLand = currentLand->next;
    }
    freePropertyList(LandProperty);

    printf("Total property value: %.2lf\n\n", totalValue);

    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
        }
        else if (input == 'r') {
            system("cls");
            calculateTotalPropertyValue(currentUser);
        }
        else if (input == 'b')
        {
            system("cls");
            generateReports(currentUser);
        }
    }
}

void insertOrUpdateUser(struct User** head, const char* name, int count)
{
    struct User* current = *head;
    while (current != NULL) {
        if (strcmp(current->name, name) == 0)
        {
            current->count += count;
            return;
        }
        current = current->next;
    }
    // If user not found, insert a new node
    struct User* newUser = malloc(sizeof(struct User));
    strcpy(newUser->name, name);
    newUser->count = count;
    newUser->next = *head;
    *head = newUser;
}

void listUsersByPropertyCount(struct User* currentUser)
{
    if (strcmp(currentUser, "admin") == 0) {
        struct User* head = NULL;

        FILE *files[6];
        files[0] = fopen("commercial_properties.txt", "r");
        files[1] = fopen("commercial_properties_rental.txt", "r");
        files[2] = fopen("land_properties.txt", "r");
        files[3] = fopen("land_properties_rental.txt", "r");
        files[4] = fopen("residential_properties.txt", "r");
        files[5] = fopen("residential_properties_rental.txt", "r");

        if (files[0] == NULL || files[1] == NULL || files[2] == NULL ||
            files[3] == NULL || files[4] == NULL || files[5] == NULL)
        {
            printf("Error opening one or more files.\n");
            usleep(300000);
            generateReports(currentUser);
        }

        int i, j;
        for (i = 0; i < 6; i++) {
            char line[256];
            while (fgets(line, sizeof(line), files[i]))
            {
                char *token = strtok(line, ",");
                if (token != NULL) {
                    token = strtok(NULL, ","); // Skip password
                    token = strtok(NULL, ","); // Get the username
                    if (token != NULL) {
                        insertOrUpdateUser(&head, token, 1);
                    }
                }
            }
            fseek(files[i], 0, SEEK_SET);
        }

        // Sort the users by count in descending order
        struct User* current = head;
        struct User* temp = NULL;
        int swapped;
        do {
            swapped = 0;
            current = head;
            while (current->next != temp) {
                if (current->count < current->next->count)
                {
                    int tempCount = current->count;
                    current->count = current->next->count;
                    current->next->count = tempCount;

                    char tempName[100];
                    strcpy(tempName, current->name);
                    strcpy(current->name, current->next->name);
                    strcpy(current->next->name, tempName);

                    swapped = 1;
                }
                current = current->next;
            }
            temp = current;
        } while (swapped);

        current = head;
        while (current != NULL) {
            printf("Username: %s, Count: %d\n", current->name, current->count);
            current = current->next;
        }

        for (i = 0; i < 6; i++) {
            fclose(files[i]);
        }
        // Free the memory allocated for the linked list
        while (head != NULL) {
            struct User* temp = head;
            head = head->next;
            free(temp);
        }

        char input;
        printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'r' && input != 'b')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
            }
            else if (input == 'r') {
                system("cls");
                listUsersByPropertyCount(currentUser);
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    } else {
        system("cls");
        printf("Access denied for non-admin users\n");

        char input;
        printf("Enter 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'b')
            {
                printf("\nPlease enter 'b' to return to the previous menu: ");
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    }
}

void listRentalPropertiesWithRestrictions(struct User* currentUser)
{
    FILE* file;
    char fileName[100];
    char propertyType[20];
    int propertyNum;

    double minPrice, maxPrice , minMortgagePrice , maxMortgagePrice;

    printf("Enter the minimum mortgage price: ");
    scanf("%lf", &minMortgagePrice);
    printf("Enter the maximum mortgage price: ");
    scanf("%lf", &maxMortgagePrice);
    printf("\nEnter the minimum rental price: ");
    scanf("%lf", &minPrice);
    printf("Enter the maximum rental price: ");
    scanf("%lf", &maxPrice);

    printf("Enter the property type (1.residential rental, 2.commercial rental): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential rental");
        snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
        break;
    case 2:
        strcpy(propertyType, "commercial rental");
        snprintf(fileName, sizeof(fileName), "commercial_properties_rental.txt");
        break;
    default:
        printf("Invalid property type!\n");
        fflush(stdin);
        usleep(300000);
        generateReports(currentUser);
    }

    file = fopen(fileName, "r");
    if (file == NULL) {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(300000);
        generateReports(currentUser);
    }

    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file))
    {
        int currentDistrict;
        sscanf(line, "%*[^,],%d,%*[^,]%*[^,]", &isActive );
        if (isActive == 1) {
            if (strcmp(propertyType, "residential rental") == 0)
            {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }
            else if (strcmp(propertyType, "commercial rental") == 0)
            {
            struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate);
            insertPropertyNode(&propertyList, property);
            }

        }
    }
    fclose(file);

    struct PropertyNode* current = propertyList;
    while (current != NULL) {
        if (strcmp(propertyType, "residential rental") == 0) {
            struct ResidentialProperty* property = (struct ResidentialProperty*)current->property;
            if (property->mortgageAmount >= minMortgagePrice && property->mortgageAmount <= maxMortgagePrice && property->monthlyRentAmount >= minPrice && property->monthlyRentAmount <= maxPrice)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Bedrooms: %d\n", property->bedrooms);
                printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
            }
        }
        else if (strcmp(propertyType, "commercial rental") == 0) {
            struct CommercialProperty* property = (struct CommercialProperty*)current->property;
            if (property->mortgageAmount >= minMortgagePrice && property->mortgageAmount <= maxMortgagePrice && property->monthlyRentalAmount >= minPrice && property->monthlyRentalAmount <= maxPrice)
            {
                printf("\nProperty ID: %d\n", property->propertyId);
                printf("Municipality District: %d\n", property->municipalityDistrict);
                printf("Address: %s\n", property->address);
                printf("Property Type: %s\n", property->propertyType);
                printf("Building Age: %d\n", property->buildingAge);
                printf("Area Size: %f\n", property->areaSize);
                printf("Floor: %d\n", property->floor);
                printf("Land Area: %f\n", property->landArea);
                printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                printf("Office Rooms: %d\n", property->officeRooms);
                printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
            }
        }
        printf("------------------\n");
        current = current->next;
    }
    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu: ");
        }
        else if (input == 'r') {
            system("cls");
            listRentalPropertiesWithRestrictions(currentUser);
        }
        else if (input == 'b')
        {
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser);
        }
    }
}
// محاسبه تفاوت زمانی با تاریخ فعلی
int calculateTimeDifference(char* lastActivity)
{
    time_t now;
    struct tm* timeinfo;
    time(&now);
    timeinfo = localtime(&now);

    int currentYear = timeinfo->tm_year + 1900;
    int currentMonth = timeinfo->tm_mon + 1;
    int currentDay = timeinfo->tm_mday;

    int lastUpdateYear, lastUpdateMonth, lastUpdateDay;
    sscanf(lastActivity, "%d-%d-%d", &lastUpdateYear, &lastUpdateMonth, &lastUpdateDay);

    int timeDifference = (currentYear - lastUpdateYear) * 365 + (currentMonth - lastUpdateMonth) * 30 + (currentDay - lastUpdateDay);
    return timeDifference;
}

void listPropertiesInSpecificMarket(struct User* currentUser)
{
    // بررسی دسترسی
    if (strcmp(currentUser, "admin") == 0)
    {
        // نام فایل مربوط به نوع ملک را بر اساس ورودی کاربر تنظیم می‌کنیم
        char fileName[100];
        int propertyNum;
        printf("Enter the property type\n(1.residential, 2.residential rental, 3.commercial, 4.commercial rental, 5.land, 6.land rental): ");
        scanf("%d", &propertyNum);

        switch (propertyNum)
        {
        case 1:
            snprintf(fileName, sizeof(fileName), "residential_properties.txt");
            break;
        case 2:
            snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
            break;
        case 3:
            snprintf(fileName, sizeof(fileName), "commercial_properties.txt");
            break;
        case 4:
            snprintf(fileName, sizeof(fileName), "commercial_properties_rental.txt");
            break;
        case 5:
            snprintf(fileName, sizeof(fileName), "land_properties.txt");
            break;
        case 6:
            snprintf(fileName, sizeof(fileName), "land_properties_rental.txt");
            break;
        default:
            printf("Invalid property type!\n");
            fflush(stdin);
            generateReports(currentUser);
        }

        // تعداد روزها را از کاربر دریافت می‌کنیم
        int days;
        printf("\nEnter the number of days for last activity: ");
        scanf("%d", &days);;
        printf("\nProperty registered in the last %d days :" , days);
        printf("\n");

        // باز کردن فایل مربوط به نوع ملک
        FILE* file = fopen(fileName, "r");
        if (file == NULL)
        {
            printf("\nFailed to open file: %s\n", fileName);
            usleep(300000);
            generateReports(currentUser);
        }

        // نمایش اطلاعات املاک در بازار خاص
        char line[300];
        char lastActivity[50];
        while (fgets(line, sizeof(line), file) != NULL)
        {
            if (propertyNum == 1) {
                sscanf(line, "%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", lastActivity);
            } else if (propertyNum == 2) {
                sscanf(line, "%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", lastActivity);
            } else if (propertyNum == 3) {
                sscanf(line, "%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", lastActivity);
            } else if (propertyNum == 4) {
                sscanf(line, "%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", lastActivity);
            } else if (propertyNum == 5) {
                sscanf(line, "%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", lastActivity);
            } else if (propertyNum == 6) {
                sscanf(line, "%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", lastActivity);
            }
            struct PropertyNode* propertyList = NULL;
            if (calculateTimeDifference(lastActivity) <= days)  // تفاوت زمانی کمتر یا مساوی تعداد روزهای ورودی
            {
                if (propertyNum == 1) {
                struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->sellingPrice, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);
                } else if (propertyNum == 3) {
                struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->sellingPrice, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Office Rooms: %d\n", property->officeRooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);
                } else if (propertyNum == 5) {
                struct LandProperty* property = malloc(sizeof(struct LandProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%s",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->landType,
                    &property->landArea, &property->distanceToMainRoad, &property->hasWell,
                    property->ownerPhoneNumber, &property->sellingPrice, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("------------------\n");
                    printf("\nProperty ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Land Type: %s\n", property->landType);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                    printf("Has Well: %d\n", property->hasWell);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);
                } else if (propertyNum == 2){
                    struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->propertyType,
                        &property->buildingAge, &property->areaSize, &property->floor,
                        &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                        &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                } else if (propertyNum == 4) {
                    struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->propertyType,
                        &property->buildingAge, &property->areaSize, &property->floor,
                        &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                        &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Office Rooms: %d\n", property->officeRooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                }
                else if (propertyNum == 6) {
                    struct LandProperty* property = malloc(sizeof(struct LandProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%lf,%s\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->landType,
                        &property->landArea, &property->distanceToMainRoad,
                        &property->hasWell, property->ownerPhoneNumber,
                        &property->mortgageAmount, &property->monthlyRentAmount,
                        property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Land Type: %s\n", property->landType);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                    printf("Has Well: %d\n", property->hasWell);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                }
            }
        }
        fclose(file);

        char input;
        printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'r' && input != 'b')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu: ");
            }
            else if (input == 'r') {
                system("cls");
                listPropertiesInSpecificMarket(currentUser);;
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    }
    else {
        system("cls");
        printf("Access denied for non-admin users\n");

        char input;
        printf("Enter 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'b')
            {
                printf("\nPlease enter 'b' to return to the previous menu: ");
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    }
}

void listApartmentsByFloor(struct User* currentUser)
{
    FILE* file;
    char fileName[100];
    char propertyType[20];
    int propertyNum;
    int floor;

    printf("Enter the Floor : ");
    scanf("%d", &floor);

    printf("Enter the property type (1.residential, 2.residential rental): ");
    scanf("%d", &propertyNum);

    switch (propertyNum)
    {
    case 1:
        strcpy(propertyType, "residential");
        snprintf(fileName, sizeof(fileName), "residential_properties.txt");
        break;
    case 2:
        strcpy(propertyType, "residential rental");
        snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
        break;
    default:
        printf("Invalid property type!\n");
        fflush(stdin);
        listApartmentsByFloor(currentUser);
    }

    file = fopen(fileName, "r");
    if (file == NULL) {
        printf("\nFailed to open file: %s\n", fileName);
        usleep(300000);
        generateReports(currentUser);
    }

    struct PropertyNode* propertyList = NULL;
    char line[300];
    int isActive;
    while (fgets(line, sizeof(line), file))
    {
        int currentFloor;
        sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%d", &isActive ,&currentFloor);
        if (isActive == 1) {
            // Create and insert the property node
            if (strcmp(propertyType, "residential") == 0) {
            struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
            sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%s\n",
                &property->propertyId, &property->isActive, property->registeredBy,
                &property->municipalityDistrict, property->address, property->propertyType,
                &property->buildingAge, &property->areaSize, &property->floor,
                &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                &property->sellingPrice, property->registrationDate);
            insertPropertyNode(&propertyList, property);
                if (strcmp(propertyType, "residential") == 0 && strcmp( property->propertyType, "Apartment") == 0 && property->floor == floor)
                {
                    printf("\nProperty ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("------------------\n");
                }
            }
            else if (strcmp(propertyType, "residential rental") == 0){
                struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                if (strcmp(propertyType, "residential rental" ) == 0 && strcmp(property->propertyType, "Apartment") == 0 && property->floor == floor)
                {
                    printf("\nProperty ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType); //assuming propertyType is correctly read and accessed from the file
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("------------------\n");
                }
            }
        }
    }
    fclose(file);

    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu: ");
        }
        else if (input == 'r') {
            system("cls");
            listApartmentsByFloor(currentUser);
        }
        else if (input == 'b')
        {
            freePropertyList(propertyList);
            system("cls");
            generateReports(currentUser);
        }
    }
}

void listDeletedPropertiesByTimeframe(struct User* currentUser)
{
    // بررسی دسترسی: فقط برای کاربر admin شامل قابلیت لیست کردن املاک است
    if (strcmp(currentUser, "admin") == 0)
    {
        // نام فایل مربوط به نوع ملک را بر اساس ورودی کاربر تنظیم می‌کنیم
        char fileName[100];
        int propertyNum;
        printf("Enter the property type\n(1.residential, 2.residential rental, 3.commercial, 4.commercial rental, 5.land, 6.land rental): ");
        scanf("%d", &propertyNum);

        switch (propertyNum)
        {
        case 1:
            snprintf(fileName, sizeof(fileName), "residential_properties.txt");
            break;
        case 2:
            snprintf(fileName, sizeof(fileName), "residential_properties_rental.txt");
            break;
        case 3:
            snprintf(fileName, sizeof(fileName), "commercial_properties.txt");
            break;
        case 4:
            snprintf(fileName, sizeof(fileName), "commercial_properties_rental.txt");
            break;
        case 5:
            snprintf(fileName, sizeof(fileName), "land_properties.txt");
            break;
        case 6:
            snprintf(fileName, sizeof(fileName), "land_properties_rental.txt");
            break;
        default:
            printf("Invalid property type!\n");
            fflush(stdin);
            generateReports(currentUser);
        }

        // تعداد روزها را از کاربر دریافت می‌کنیم
        int days;
        printf("\nEnter the number of days for last activity: ");
        scanf("%d", &days);;
        printf("\nProperties archived in the last %d day: " , days);
        printf("\n");

        // باز کردن فایل مربوط به نوع ملک
        FILE* file = fopen(fileName, "r");
        if (file == NULL)
        {
            printf("\nFailed to open file: %s\n", fileName);
            usleep(300000);
            generateReports(currentUser);
        }

        // نمایش اطلاعات املاک در بازار خاص
        char line[300];
        int isActive;
        char lastActivity[50];
        while (fgets(line, sizeof(line), file) != NULL)
        {
            if (propertyNum == 1) {
                sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]",&isActive, lastActivity);
            } else if (propertyNum == 2) {
                sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", &isActive, lastActivity);
            } else if (propertyNum == 3) {
                sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", &isActive, lastActivity);
            } else if (propertyNum == 4) {
                sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", &isActive, lastActivity);
            } else if (propertyNum == 5) {
                sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", &isActive, lastActivity);
            } else if (propertyNum == 6) {
                sscanf(line, "%*[^,],%d,%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%*[^,],%[^,]", &isActive, lastActivity);
            }
            struct PropertyNode* propertyList = NULL;
            if (isActive == 0 && calculateTimeDifference(lastActivity) <= days)  // تفاوت زمانی کمتر یا مساوی تعداد روزهای ورودی
            {
                if (propertyNum == 1) {
                struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%[^,],%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->sellingPrice, property->registrationDate,property->deleteDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);
                    printf("Property archive time: %s\n", property->deleteDate);
                } else if (propertyNum == 3) {
                struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%[^,],%s\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->sellingPrice, property->registrationDate, property->deleteDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Office Rooms: %d\n", property->officeRooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);
                    printf("Property archive time: %s\n", property->deleteDate);
                } else if (propertyNum == 5) {
                struct LandProperty* property = malloc(sizeof(struct LandProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%[^,],%s",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->landType,
                    &property->landArea, &property->distanceToMainRoad, &property->hasWell,
                    property->ownerPhoneNumber, &property->sellingPrice, property->registrationDate, property->deleteDate);
                insertPropertyNode(&propertyList, property);
                    printf("------------------\n");
                    printf("\nProperty ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Land Type: %s\n", property->landType);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                    printf("Has Well: %d\n", property->hasWell);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);
                    printf("Property archive time: %s\n", property->deleteDate);
                }
                else if (propertyNum == 2)
                {
                    struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%[^,],%s\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->propertyType,
                        &property->buildingAge, &property->areaSize, &property->floor,
                        &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                        &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate, property->deleteDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                    printf("Property archive time: %s\n", property->deleteDate);
                } else if (propertyNum == 4) {
                    struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%[^,],%s\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->propertyType,
                        &property->buildingAge, &property->areaSize, &property->floor,
                        &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                        &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate, property->deleteDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Office Rooms: %d\n", property->officeRooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                    printf("Property archive time: %s\n", property->deleteDate);
                }
                else if (propertyNum == 6) {
                    struct LandProperty* property = malloc(sizeof(struct LandProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%lf,%[^,],%s\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->landType,
                        &property->landArea, &property->distanceToMainRoad,
                        &property->hasWell, property->ownerPhoneNumber,
                        &property->mortgageAmount, &property->monthlyRentAmount,
                        property->registrationDate, property->deleteDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Land Type: %s\n", property->landType);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                    printf("Has Well: %d\n", property->hasWell);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                    printf("Property archive time: %s\n", property->deleteDate);
                }
            }
        }
        fclose(file);

        char input;
        printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'r' && input != 'b')
            {
                printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu. ");
            }
            else if (input == 'r') {
                system("cls");
                listDeletedPropertiesByTimeframe(currentUser);
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    } else {
        system("cls");
        printf("Access denied for non-admin users\n");

        char input;
        printf("Enter 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'b')
            {
                printf("\nPlease enter 'b' to return to the previous menu: ");
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    }
}

void listUsersAndLastActivity(struct User* currentUser)
{
    if (strcmp(currentUser, "admin") == 0)
    {
        FILE* file = fopen("users.txt", "r");
        if (file != NULL)
        {
            char line[256];
            while (fgets(line, sizeof(line), file))
            {
                char tempUsername[50];
                char activityTime[50];
                sscanf(line, "%s %*s %*s %*s %*s %*s %*s %s", tempUsername, activityTime);
                printf("%s : %s\n", tempUsername, activityTime);
            }
            fclose(file);
            char input;
            printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
                while (1)
                {
                    input = getche();
                    fflush(stdin); // برای خالی کردن buffer ورودی

                    if (input != 'r' && input != 'b')
                    {
                        printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu: ");
                    }
                    else if (input == 'r') {
                        system("cls");
                        listUsersAndLastActivity(currentUser);
                    }
                    else if (input == 'b')
                    {
                        system("cls");
                        generateReports(currentUser);
                    }
                }
        }
        else
        {
            printf("Error opening file\n");
        }
    }
    else {
        system("cls");
        printf("Access denied for non-admin users\n");

        char input;
        printf("Enter 'b' to return to the previous menu:");
        while (1)
        {
            input = getche();

            if (input != 'b')
            {
                printf("\nPlease enter 'b' to return to the previous menu: ");
            }
            else if (input == 'b')
            {
                system("cls");
                generateReports(currentUser);
            }
        }
    }
}

void PropertiesRegisteredByCurrentUser(struct User *currentUser)
{
    char *propertyFiles[] =
    {
        "residential_properties.txt",
        "commercial_properties.txt",
        "land_properties.txt",
        "residential_properties_rental.txt",
        "commercial_properties_rental.txt",
        "land_properties_rental.txt"
    };
    char *propertyNames[] =
    {
        "Residential properties ",
        "Commercial properties",
        "Land properties",
        "Residential properties rental",
        "Commercial properties rental",
        "Land properties rental"
    };

    for (int i = 0; i < 6; i++) {
        FILE *file = fopen(propertyFiles[i], "r");
        printf("\n------------------\n");
        printf("\n**%s**\n", propertyNames[i]);
        if (file == NULL) {
            printf("\nFailed to open file: %s\n", propertyFiles[i]);
            continue;
        }

        char line[300];
        while (fgets(line, sizeof(line), file)) {
            char *registeredBy = (char *)malloc(50 * sizeof(char));
            sscanf(line, "%*d,%*d,%[^,]", registeredBy);
            struct PropertyNode* propertyList = NULL;
            if (strcmp(registeredBy, currentUser->username) == 0)
            {
                if (strcmp(propertyFiles[i], "residential_properties.txt") == 0)
                {
                struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%[^,]\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                    &property->sellingPrice, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Is active: %d\n", property->isActive);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);

                } else if (strcmp(propertyFiles[i], "commercial_properties.txt") == 0) {
                struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%[^,]\n",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->propertyType,
                    &property->buildingAge, &property->areaSize, &property->floor,
                    &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                    &property->sellingPrice, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Is active: %d\n", property->isActive);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Office Rooms: %d\n", property->officeRooms);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);

                } else if (strcmp(propertyFiles[i], "land_properties.txt") == 0) {
                struct LandProperty* property = malloc(sizeof(struct LandProperty));
                sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%[^,]",
                    &property->propertyId, &property->isActive, property->registeredBy,
                    &property->municipalityDistrict, property->address, property->landType,
                    &property->landArea, &property->distanceToMainRoad, &property->hasWell,
                    property->ownerPhoneNumber, &property->sellingPrice, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("------------------\n");
                    printf("\nProperty ID: %d\n", property->propertyId);
                    printf("Is active: %d\n", property->isActive);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Land Type: %s\n", property->landType);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                    printf("Has Well: %d\n", property->hasWell);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Selling Price: %lf\n", property->sellingPrice);
                    printf("Property registration time: %s\n", property->registrationDate);

                }
                else if (strcmp(propertyFiles[i], "residential_properties_rental.txt") == 0)
                {
                    struct ResidentialProperty* property = malloc(sizeof(struct ResidentialProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%[^,]\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->propertyType,
                        &property->buildingAge, &property->areaSize, &property->floor,
                        &property->landArea, property->ownerPhoneNumber, &property->bedrooms,
                        &property->mortgageAmount, &property->monthlyRentAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Is active: %d\n", property->isActive);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Bedrooms: %d\n", property->bedrooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("Property registration time: %s\n", property->registrationDate);

                } else if (strcmp(propertyFiles[i], "commercial_properties_rental.txt") == 0) {
                    struct CommercialProperty* property = malloc(sizeof(struct CommercialProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%[^,],%d,%lf,%lf,%[^,]\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->propertyType,
                        &property->buildingAge, &property->areaSize, &property->floor,
                        &property->landArea, property->ownerPhoneNumber, &property->officeRooms,
                        &property->monthlyRentalAmount, &property->mortgageAmount, property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Is active: %d\n", property->isActive);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Property Type: %s\n", property->propertyType);
                    printf("Building Age: %d\n", property->buildingAge);
                    printf("Area Size: %f\n", property->areaSize);
                    printf("Floor: %d\n", property->floor);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Office Rooms: %d\n", property->officeRooms);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rental Amount: %lf\n", property->monthlyRentalAmount);
                    printf("Property registration time: %s\n", property->registrationDate);

                }
                else if (strcmp(propertyFiles[i], "land_properties_rental.txt") == 0) {
                    struct LandProperty* property = malloc(sizeof(struct LandProperty));
                    sscanf(line, "%d,%d,%[^,],%d,%[^,],%[^,],%f,%f,%d,%[^,],%lf,%lf,%[^,]\n",
                        &property->propertyId, &property->isActive, property->registeredBy,
                        &property->municipalityDistrict, property->address, property->landType,
                        &property->landArea, &property->distanceToMainRoad,
                        &property->hasWell, property->ownerPhoneNumber,
                        &property->mortgageAmount, &property->monthlyRentAmount,
                        property->registrationDate);
                insertPropertyNode(&propertyList, property);
                    printf("\n------------------\n");
                    printf("Property ID: %d\n", property->propertyId);
                    printf("Is active: %d\n", property->isActive);
                    printf("Municipality District: %d\n", property->municipalityDistrict);
                    printf("Address: %s\n", property->address);
                    printf("Land Type: %s\n", property->landType);
                    printf("Land Area: %f\n", property->landArea);
                    printf("Distance to Main Road: %f\n", property->distanceToMainRoad);
                    printf("Has Well: %d\n", property->hasWell);
                    printf("Owner Phone Number: %s\n", property->ownerPhoneNumber);
                    printf("Mortgage Amount: %lf\n", property->mortgageAmount);
                    printf("Monthly Rent Amount: %lf\n", property->monthlyRentAmount);
                    printf("Property registration time: %s\n", property->registrationDate);
                }
            free(registeredBy);
            }
        }
        fclose(file);
    }

    char input;
    printf("\nEnter 'r' to use again or 'b' to return to the previous menu:");
    while (1)
    {
        input = getche();
        fflush(stdin);

        if (input != 'r' && input != 'b')
        {
            printf("\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bPlease enter 'r' to reuse or 'b' to go back to the previous menu: ");
        }
        else if (input == 'r') {
            system("cls");
            PropertiesRegisteredByCurrentUser(currentUser);
        }
        else if (input == 'b')
        {
            system("cls");
            generateReports(currentUser);
        }
    }
}

void viewProfile(const char* username) // تابع برای نمایش پروفایل کاربر (اسم ، وایمیل و ...)
{
    FILE* userFile = fopen("users.txt", "r");
    if (userFile != NULL) {
        char line[255];
        while (fgets(line, sizeof(line), userFile) != NULL) {
            char savedUsername[50], password[50], name[50], lastName[50], phoneNumber[20], nationalCode[20], email[50];
            sscanf(line, "%s %s %s %s %s %s %s", savedUsername, password, name, lastName, phoneNumber, nationalCode, email);
            if (strcmp(savedUsername, username) == 0) {
                printf("Name: %s\n", name);
                printf("Last Name: %s\n", lastName);
                printf("Phone Number: %s\n", phoneNumber);
                printf("National Code: %s\n", nationalCode);
                printf("Email: %s\n", email);
                break;
            }
        }
        fclose(userFile);
    } else {
        printf("Error: Failed to open user file.\n");
    }
    printf("\n>>Press any key to go back to the previous menu: ");
    getch();
    system("cls");
    mainMenu(username);
}

// توابع زیر برای بخش تنظیمات برنامه هستند

int checkCurrentPassword(char* currentPassword, char* enteredUsername)
{
    FILE *file = fopen("users.txt", "r");
    if (file != NULL) {
        char line[100];
        char *token;

        while (fgets(line, sizeof(line), file) != NULL)
        {
            // جدا کردن نام کاربری و رمز عبور
            token = strtok(line, " ");
            char fileUsername[50];
            strcpy(fileUsername, token);

            token = strtok(NULL, " ");
            char filePassword[50];
            strcpy(filePassword, token);

            // حذف کاراکتر جدید خط
            filePassword[strcspn(filePassword, "\n")] = 0;

            if (strcmp(fileUsername, enteredUsername) == 0 && strcmp(filePassword, currentPassword) == 0) {
                fclose(file);
                return 1;
            }
        }
        fclose(file);
    }
    return 0;
}

void changePassword(struct User* currentUser)
{
    char enteredPassword[50];
    char newPassword[50];
    char confirmedNewPassword[50];

    printf("Enter your current password: ");
    scanf("%s" , enteredPassword);

    if (checkCurrentPassword(enteredPassword, currentUser->username) == 0)
    {
        printf("\nIncorrect password. Please try again.\n");
        changePassword(currentUser);
        return;
    }

    printf("\nEnter your new password: ");
    hidePassword(newPassword);

    if (strcmp(newPassword, enteredPassword) == 0)
    {
        printf("\n**New password should be different from the current password! Please try again.\n");
        changePassword(currentUser);
        return;
    }

    printf("\nConfirm your new password: ");
    hidePassword(confirmedNewPassword);
    printf("\n");

    if (strcmp(newPassword, confirmedNewPassword) != 0)
    {
        printf("Passwords do not match. Please try again.\n");
        changePassword(currentUser);
        return;
    }

    FILE* originalFile = fopen("users.txt", "r");
    FILE* tempFile = fopen("temp.txt", "w");

    if (originalFile != NULL && tempFile != NULL)
    {
        char username[50];
        char password[50];
        char name[50];
        char lastName[50];
        char phoneNumber[50];
        char nationalCode[50];
        char email[50];
        char lastLogin[50];
        int userFound = 0;

        while (fscanf(originalFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin) != EOF)
        {
            if (strcmp(username, currentUser->username) == 0) {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, newPassword, name, lastName, phoneNumber, nationalCode, email, lastLogin);
                userFound = 1;
            } else {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin);
            }
        }

        fclose(originalFile);
        fclose(tempFile);

        if (userFound)
        {
            if (remove("users.txt") == 0) {
                if (rename("temp.txt", "users.txt") == 0)
                {
                    printf("Password updated successfully");
                    for (int i = 0; i < 5; i++)
                    {
                        printf(".");
                        usleep(300000);
                    }
                    system("cls");
                    mainMenu(currentUser);
                } else {
                    printf("Error renaming file.\n");
                }
            } else {
                printf("Error removing file.\n");
            }
        } else
        {
            printf("User not found in file.\n");
            changePassword(currentUser);
            return;
        }
    }
    else {
        printf("Error handling files.\n");
    }
}

void changeName(struct User* currentUser)
{
    char newName[50];
    printf("Enter new name: ");
    scanf("%s", newName);

    // Write user data back to file
    FILE* originalFile = fopen("users.txt", "r");
    FILE* tempFile = fopen("temp.txt", "w");

    if (originalFile != NULL && tempFile != NULL)
    {
        char username[50];
        char password[50];
        char name[50];
        char lastName[50];
        char phoneNumber[50];
        char nationalCode[50];
        char email[50];
        char lastLogin[50];
        int userFound = 0;

        while (fscanf(originalFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin) != EOF)
        {
            if (strcmp(username, currentUser->username) == 0)
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, newName, lastName, phoneNumber, nationalCode, email, lastLogin);
                userFound = 1;
            }
            else
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin);
            }
        }

        fclose(originalFile);
        fclose(tempFile);

        if (userFound)
        {
            if (remove("users.txt") == 0)
            {
                if (rename("temp.txt", "users.txt") == 0)
                {
                    printf("Name updated successfully");
                    for (int i = 0; i < 5; i++)
                    {
                        printf(".");
                        usleep(300000);
                    }
                    system("cls");
                    mainMenu(currentUser);
                }
                else
                {
                    printf("Error renaming file.\n");
                }
            }
            else
            {
                printf("Error removing file.\n");
            }
        }
        else
        {
            printf("User not found in file.\n");
            changeName(currentUser);
            return;
        }
    }
    else
    {
        printf("Error handling files.\n");
    }
}


void changeLastName(struct User* currentUser)
{
    char newLastName[50];
    printf("Enter new last name: ");
    scanf("%s", newLastName);

    FILE* originalFile = fopen("users.txt", "r");
    FILE* tempFile = fopen("temp.txt", "w");

    if (originalFile != NULL && tempFile != NULL)
    {
        char username[50];
        char password[50];
        char name[50];
        char lastName[50];
        char phoneNumber[50];
        char nationalCode[50];
        char email[50];
        char lastLogin[50];
        int userFound = 0;

        while (fscanf(originalFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin) != EOF)
        {
            if (strcmp(username, currentUser->username) == 0)
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, newLastName, phoneNumber, nationalCode, email, lastLogin);
                userFound = 1;
            }
            else
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin);
            }
        }

        fclose(originalFile);
        fclose(tempFile);

        if (remove("users.txt") == 0 && rename("temp.txt", "users.txt") == 0) {
            printf("Last name updated successfully");
            for (int i = 0; i < 5; i++)
            {
                printf(".");
                usleep(300000);
            }
            system("cls");
            mainMenu(currentUser);
        } else {
            printf("Error updating last name\n");
            mainMenu(currentUser);
            return;
        }
    } else {
        printf("Error handling files.\n");
    }
}

void changeEmail(struct User* currentUser)
{
    char newEmail[50];
    printf("Enter new email: ");
    scanf("%s", newEmail);
    if (!isValidEmail(newEmail))
    {
        printf("Invalid email format.\n");
        changeEmail(currentUser);  // Call the function again
        return;
    }

    FILE* originalFile = fopen("users.txt", "r");
    FILE* tempFile = fopen("temp.txt", "w");

    if (originalFile != NULL && tempFile != NULL)
    {
        char username[50];
        char password[50];
        char name[50];
        char lastName[50];
        char phoneNumber[50];
        char nationalCode[50];
        char email[50];
        char lastLogin[50];
        int userFound = 0;

        while (fscanf(originalFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin) != EOF)
        {
            if (strcmp(username, currentUser->username) == 0)
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, newEmail, lastLogin);
                userFound = 1;
            }
            else
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin);
            }
        }

        fclose(originalFile);
        fclose(tempFile);

        if (userFound)
        {
            if (remove("users.txt") == 0)
            {
                if (rename("temp.txt", "users.txt") == 0)
                {
                    printf("Email updated successfully");
                    for (int i = 0; i < 5; i++)
                    {
                        printf(".");
                        usleep(300000);
                    }
                    system("cls");
                    mainMenu(currentUser);
                    return;
                }
                else
                {
                    printf("Error renaming file.\n");
                }
            }
            else
            {
                printf("Error removing file.\n");
            }
        }
        else
        {
            printf("User not found in file.\n");
            changeEmail(currentUser);
            return;
        }
    }
    else
    {
        printf("Error handling files.\n");
    }
}

void changePhoneNumber(struct User* currentUser)
{
    char newPhoneNumber[50];
    printf("Enter new phone number (11 digits): ");
    scanf("%s", newPhoneNumber);

    if (!isValidPhoneNumber(newPhoneNumber))
    {
        printf("Invalid phone number format.\n");
        changePhoneNumber(currentUser);
        return;
    }

    FILE* originalFile = fopen("users.txt", "r");
    FILE* tempFile = fopen("temp.txt", "w");

    if (originalFile != NULL && tempFile != NULL)
    {
        char username[50];
        char password[50];
        char name[50];
        char lastName[50];
        char phoneNumber[50];
        char nationalCode[50];
        char email[50];
        char lastLogin[50];
        int userFound = 0;

        while (fscanf(originalFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin) != EOF)
        {
            if (strcmp(username, currentUser->username) == 0)
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, newPhoneNumber, nationalCode, email, lastLogin);
                userFound = 1;
            }
            else
            {
                fprintf(tempFile, "%s %s %s %s %s %s %s %s\n", username, password, name, lastName, phoneNumber, nationalCode, email, lastLogin);
            }
        }

        fclose(originalFile);
        fclose(tempFile);

        if (userFound)
        {
            if (remove("users.txt") == 0)
            {
                if (rename("temp.txt", "users.txt") == 0)
                {
                    printf("Phone number updated successfully");
                    for (int i = 0; i < 5; i++)
                    {
                        printf(".");
                        usleep(300000);
                    }
                    system("cls");
                    mainMenu(currentUser);
                }
                else
                {
                    printf("Error renaming file.\n");
                }
            }
            else
            {
                printf("Error removing file.\n");
            }
        }
        else
        {
            printf("User not found in file.\n");
            changePhoneNumber(currentUser);
            return;
        }
    }
    else
    {
        printf("Error handling files.\n");
    }
}
