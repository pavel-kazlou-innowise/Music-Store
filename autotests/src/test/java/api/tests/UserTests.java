package api.tests;

import api.model.User;
import api.model.UserModel;
import io.restassured.http.ContentType;
import io.restassured.response.ValidatableResponse;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static api.endpoints.Endpoints.*;
import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static utils.TestDataUtils.getGeneratedEmail;
import static utils.TestDataUtils.getGeneratedName;

@Log4j2
public class UserTests extends BaseTest {
    private final String email = getGeneratedEmail();
    private final String username = getGeneratedName();
    private final String password = "password";
    User newUser;
    UserModel user = new UserModel(email, username, password);

    @Test()
    public void verifyUserCreationTest() {
        newUser = given()
                .contentType(ContentType.JSON)
                .body(user)
                .when()
                .post(BASE_URL + API + REGISTER)
                .then().statusCode(200)
                .extract().as(User.class);
        log.info("New User with id {} and name {} was created", newUser.getId(), newUser.getUsername());
        assertTrue(email.equalsIgnoreCase(newUser.getEmail()));
        assertEquals(username, newUser.getUsername());
    }

    @Test()
    public void changeUserRightsTest() {
        Map<String, Object> requestBody = Map.of("is_admin", true);
        User updatedUser = authenticatedAsAdminRequest()
                .body(requestBody)
                .when()
                .patch(String.format(BASE_URL + API + USERS_USERNAME_RIGHTS, "Tester"))
                .then()
                .statusCode(200)
                .extract().as(User.class);
        assertEquals("true", updatedUser.getIs_admin());
        requestBody = Map.of("is_admin", false);
        updatedUser = authenticatedAsAdminRequest()
                .body(requestBody)
                .when()
                .patch(String.format(BASE_URL + API + USERS_USERNAME_RIGHTS, "Tester"))
                .then()
                .statusCode(200)
                .extract().as(User.class);
        assertEquals("false", updatedUser.getIs_admin());
    }

    @Test()
    public void changeUserRightsWithoutAuthorizationTest() {
        Map<String, Object> requestBody = Map.of("is_admin", true);
        ValidatableResponse response = given()
                .body(requestBody)
                .when()
                .patch(String.format(BASE_URL + API + USERS_USERNAME_RIGHTS, "Tester"))
                .then()
                .statusCode(401);
    }

    @Test()
    public void changeUserRightsAsUserWithoutAdminRightsTest() {
        Map<String, Object> requestBody = Map.of("is_admin", true);
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .body(requestBody)
                .when()
                .patch(String.format(BASE_URL + API + USERS_USERNAME_RIGHTS, "Tester"))
                .then()
                .statusCode(403);
    }

    @Test()
    public void changeUserRightsWithInvalidDataTest() {
        Map<String, Object> requestBody = Map.of("is_admin", "test");
        ValidatableResponse response = authenticatedAsAdminRequest()
                .body(requestBody)
                .when()
                .patch(String.format(BASE_URL + API + USERS_USERNAME_RIGHTS, "Tester"))
                .then()
                .statusCode(422);
    }
}
