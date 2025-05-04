package api.tests;

import api.model.Token;
import api.model.UserModel;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.BeforeAll;

import static api.endpoints.Endpoints.*;
import static io.restassured.RestAssured.given;

@Log4j2
public class BaseTest {

    public static UserModel adminUser = new UserModel("Lida", "Lida");
    public static UserModel simpleUser = new UserModel("TestUser", "TestUser");
    public static Token adminToken;
    public static Token simpleUserToken;

    @BeforeAll
    public static void authorizeUsersAndGetTokens() {
        RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
        getAdminToken();
        getSimpleUserToken();
    }

    public static void getAdminToken() {
        adminToken = given()
                .contentType(ContentType.URLENC)
                .formParam("username", adminUser.getUsername())
                .formParam("password", adminUser.getPassword())
                .when()
                .post(BASE_URL + API + TOKEN)
                .then().statusCode(200)
                .extract().as(Token.class);
        log.info("Token was extracted and value is: {}", adminToken.getAccess_token());
    }

    public static void getSimpleUserToken() {
        simpleUserToken = given()
                .contentType(ContentType.URLENC)
                .formParam("username", simpleUser.getUsername())
                .formParam("password", simpleUser.getPassword())
                .when()
                .post(BASE_URL + API + TOKEN)
                .then().statusCode(200)
                .extract().as(Token.class);
        log.info("Token was extracted and value is: {}", simpleUserToken.getAccess_token());
    }

    protected RequestSpecification authenticatedAsAdminRequest() {
        return given()
                .contentType(ContentType.JSON)
                .header("Authorization", "Bearer " + adminToken.getAccess_token());
    }

    protected RequestSpecification authenticatedAsNotAdminRequest() {
        return given()
                .contentType(ContentType.JSON)
                .header("Authorization", "Bearer " + simpleUserToken.getAccess_token());
    }
}
