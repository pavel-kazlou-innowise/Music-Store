package api.tests;

import api.model.*;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.BeforeAll;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

import static api.endpoints.Endpoints.*;
import static io.restassured.RestAssured.given;
import static utils.TestDataUtils.*;

@Log4j2
public class BaseTest {

    private static final UserModel ADMIN_USER_MODEL = new UserModel(getGeneratedEmail(), "AdminUser", "AdminUser123#");
    private static final UserModel TEST_USER_MODEL = new UserModel(getGeneratedEmail(), "TestUser", "TestUser123#");
    public final static ArtistModel ARTIST_MODEL = new ArtistModel(getGeneratedName(), getGeneratedDescription());
    public static Artist testArtist;
    public static User adminUser;
    public static User simpleUser;
    public static Token adminToken;
    public static Token simpleUserToken;

    @BeforeAll
    public static void prepareUsersContentAndEnvironment() throws IOException, InterruptedException {
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
        clearDatabase();
        createAdminUser();
        createSimpleUser();
        log.info("Authorize AdminUser and get token");
        getAdminToken();
        log.info("Authorize User and get token");
        getSimpleUserToken();
        createTestArtist();
    }

    public static void getAdminToken() {
        adminToken = given()
                .contentType(ContentType.URLENC)
                .formParam("username", ADMIN_USER_MODEL.getUsername())
                .formParam("password", ADMIN_USER_MODEL.getPassword())
                .post(BASE_URL + API + TOKEN)
                .then().statusCode(200)
                .extract().as(Token.class);
        System.out.println(adminToken.getAccess_token());
        log.info("Token was extracted and value is: {}", adminToken.getAccess_token());
    }

    public static void getSimpleUserToken() {
        simpleUserToken = given()
                .contentType(ContentType.URLENC)
                .formParam("username", TEST_USER_MODEL.getUsername())
                .formParam("password", TEST_USER_MODEL.getPassword())
                .when()
                .post(BASE_URL + API + TOKEN)
                .then().statusCode(200)
                .extract().as(Token.class);
        log.info("Token was extracted and value is: {}", simpleUserToken.getAccess_token());
    }

    public static void clearDatabase() throws IOException, InterruptedException {
        String testRoot = System.getProperty("user.dir");
        String projectRoot = new File(testRoot).getParent();
        String pythonScript = STR."\{projectRoot}\{File.separator}clear_db.py";

        ProcessBuilder processBuilder = new ProcessBuilder("python", pythonScript);
        processBuilder.redirectErrorStream(true);

        processBuilder.directory(new File(projectRoot));

        Process process = processBuilder.start();

        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("[Python] " + line);
            }
        }

        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Failed to clear database. Exit code: " + exitCode);
        }
    }

    protected static RequestSpecification authenticatedAsAdminRequest() {
        return given()
                .contentType(ContentType.JSON)
                .header("Authorization", "Bearer " + adminToken.getAccess_token());
    }

    protected RequestSpecification authenticatedAsNotAdminRequest() {
        return given()
                .contentType(ContentType.JSON)
                .header("Authorization", "Bearer " + simpleUserToken.getAccess_token());
    }

    public static void createAdminUser() {
        log.info("Creation of adminUser started");
        adminUser = given()
                .contentType(ContentType.JSON)
                .body(ADMIN_USER_MODEL)
                .when()
                .post(BASE_URL + API + REGISTER)
                .then().statusCode(200)
                .extract().as(User.class);
        log.info("New User with id {} and name {} was created", adminUser.getId(), adminUser.getUsername());
    }

    public static void createSimpleUser() {
        log.info("Creation of simpleUser started");
        simpleUser = given()
                .contentType(ContentType.JSON)
                .body(TEST_USER_MODEL)
                .when()
                .post(BASE_URL + API + REGISTER)
                .then().statusCode(200)
                .extract().as(User.class);
        log.info("New User with id {} and name {} was created", simpleUser.getId(), simpleUser.getUsername());
    }

    public static void createTestArtist() {
        testArtist = authenticatedAsAdminRequest()
                .body(ARTIST_MODEL)
                .when()
                .post(BASE_URL + API + ARTISTS)
                .then().statusCode(200)
                .extract().as(Artist.class);
        log.info("Artist with id {} and name {} was created", testArtist.getId(), testArtist.getName());
    }
}
