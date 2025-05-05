package api.tests;

import api.model.Artist;
import api.model.ArtistModel;
import io.restassured.common.mapper.TypeRef;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.response.ValidatableResponse;
import lombok.extern.log4j.Log4j2;

import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.stream.Collectors;

import static api.endpoints.Endpoints.*;
import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static utils.TestDataUtils.*;

@Log4j2
public class ArtistsTests extends BaseTest {

    @Test
    public void createNewArtistTest() {
        ArtistModel artist = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        Artist newArtist = authenticatedAsAdminRequest()
                .body(artist)
                .when()
                .post(BASE_URL + API + ARTISTS)
                .then().statusCode(201)
                .extract().as(Artist.class);
        assertEquals(artist.getName(), newArtist.getName(), "The name of created artist is incorrect");
        assertEquals(artist.getDescription(), newArtist.getDescription(), "The description of created artist is incorrect");
        log.info("Artist with id {} and name {} was created", newArtist.getId(), newArtist.getName());
    }

    @Test
    public void createNewArtistWithoutAuthorizationTest() {
        ArtistModel artist = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        ValidatableResponse newArtist = given()
                .contentType(ContentType.JSON)
                .body(artist)
                .when()
                .post(BASE_URL + API + ARTISTS)
                .then().statusCode(401);
    }

    @Test
    public void createNewArtistAsNotAdminTest() {
        ArtistModel artist = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .body(artist)
                .when()
                .post(BASE_URL + API + ARTISTS)
                .then().statusCode(403);
    }

    @Test
    public void createNewArtistWithInvalidDataTest() {
        ArtistModel artist = new ArtistModel("", getGeneratedDescription());
        ValidatableResponse response = authenticatedAsAdminRequest()
                .body(artist)
                .when()
                .post(BASE_URL + API + ARTISTS)
                .then().statusCode(422);
    }

    @Test
    public void getListOfArtistsTest() {
        List<Artist> artists = authenticatedAsAdminRequest()
                .queryParam("skip", 0)
                .queryParam("limit", 100)
                .when()
                .get(BASE_URL + API + ARTISTS).then().statusCode(200)
                .extract().as(new TypeRef<List<Artist>>() {
                });
        assertFalse(artists.isEmpty(), "The list of artists is empty");
        log.info("The list of artists is: {}",
                artists.stream()
                        .map(artist -> String.format("Name: %s, Description: %s, ID: %s", artist.getName(), artist.getDescription(), artist.getId()))
                        .collect(Collectors.joining("; ")));
    }

    @Test
    public void getListOfArtistsWithoutAuthorizationTest() {
        ValidatableResponse response = given()
                .when()
                .get(BASE_URL + API + ARTISTS).then().statusCode(401);
    }

    @Test
    public void getListOfArtistsAsUserWithoutAdminRightsTest() {
        List<Artist> artists = authenticatedAsNotAdminRequest()
                .queryParam("skip", 0)
                .queryParam("limit", 100)
                .when()
                .get(BASE_URL + API + ARTISTS).then().statusCode(200)
                .extract().as(new TypeRef<List<Artist>>() {
                });
        assertFalse(artists.isEmpty(), "The list of artists is empty");
        log.info("The list of artists is: {}",
                artists.stream()
                        .map(artist -> String.format("Name: %s, Description: %s, ID: %s", artist.getName(), artist.getDescription(), artist.getId()))
                        .collect(Collectors.joining("; ")));
    }

    @Test
    public void getListOfArtistsWithInvalidRequestParametersTest() {
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .queryParam("skip", "test")
                .queryParam("limit", "test")
                .when()
                .get(BASE_URL + API + ARTISTS).then().statusCode(422);
    }

    @Test
    public void getArtistByIdTest() {
        Artist artistTest = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ARTISTS + "5")
                .then().statusCode(200)
                .extract().as(Artist.class);
        assertEquals("test", artistTest.getName(), "The name of artist is incorrect");
        assertEquals("test", artistTest.getDescription(), "The description artist is incorrect");
        log.info("Artist with id {} and name {} was found", artistTest.getId(), artistTest.getName());
    }

    @Test
    public void getAlbumAsNoAuthorizedTest() {
        ValidatableResponse response = given()
                .when()
                .get(BASE_URL + API + ARTISTS + "5")
                .then().statusCode(401);
    }

    @Test
    public void getArtistAsUserWithoutAdminRightsTest() {
        Artist artistTest = authenticatedAsNotAdminRequest()
                .when()
                .get(BASE_URL + API + ARTISTS + "5")
                .then().statusCode(200)
                .extract().as(Artist.class);
        assertEquals("test", artistTest.getName(), "The name of artist is incorrect");
        assertEquals("test", artistTest.getDescription(), "The description artist is incorrect");
        log.info("Artist with id {} and name {} was found", artistTest.getId(), artistTest.getName());
    }

    @Test
    public void getArtistByInvalidIdTest() {
        ValidatableResponse response = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ARTISTS + "0")
                .then().statusCode(404);
    }

    @Test
    public void updateArtistTest() {
        ArtistModel artistForUpdate = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        Artist updatedArtist = authenticatedAsAdminRequest()
                .body(artistForUpdate)
                .when()
                .put(BASE_URL + API + ARTISTS + 5)
                .then().statusCode(200)
                .extract().as(Artist.class);
        log.info("Artist's name after update is: {} and description is: {}", updatedArtist.getName(), artistForUpdate.getDescription());
        assertEquals(artistForUpdate.getName(), updatedArtist.getName(), "The name of updated artist is incorrect");
        assertEquals(artistForUpdate.getDescription(), updatedArtist.getDescription(), "The description of updated artist is incorrect");
        // return previous data
        artistForUpdate.setName("test");
        artistForUpdate.setDescription("test");
        Response response = authenticatedAsAdminRequest()
                .body(artistForUpdate)
                .when()
                .put(BASE_URL + API + ARTISTS + 5);
        response.then().statusCode(200);
    }

    @Test
    public void updateArtistWithoutAuthorizationTest() {
        ArtistModel artistForUpdate = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        ValidatableResponse updatedArtist = given()
                .contentType(ContentType.JSON)
                .body(artistForUpdate)
                .when()
                .put(BASE_URL + API + ARTISTS + 5)
                .then().statusCode(401);
    }

    @Test
    public void updateArtistAsNotAminTest() {
        ArtistModel artistForUpdate = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        ValidatableResponse updatedArtist = authenticatedAsNotAdminRequest()
                .body(artistForUpdate)
                .when()
                .put(BASE_URL + API + ARTISTS + 5)
                .then().statusCode(403);
    }

    @Test
    public void updateArtistWithInvalidDataTest() {
        ArtistModel artistForUpdate = new ArtistModel("", getGeneratedDescription());
        ValidatableResponse updatedArtist = authenticatedAsAdminRequest()
                .body(artistForUpdate)
                .when()
                .put(BASE_URL + API + ARTISTS + 5)
                .then().statusCode(422);
    }

    @Test
    public void updateInvalidArtistTest() {
        ArtistModel artistForUpdate = new ArtistModel(getGeneratedName(), getGeneratedDescription());
        ValidatableResponse updatedArtist = authenticatedAsAdminRequest()
                .body(artistForUpdate)
                .when()
                .put(BASE_URL + API + ARTISTS + 0)
                .then().statusCode(404);
    }

    @Test
    public void deleteArtistTest() {
        List<Artist> artists = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ARTISTS)
                .body().as(new TypeRef<List<Artist>>() {
                });
        Artist artistToDelete = artists.stream()
                .filter(artist -> artist.getName() != null && artist.getName().startsWith("AT_"))
                .findFirst().orElse(null);
        ValidatableResponse response = authenticatedAsAdminRequest()
                .delete(BASE_URL + API + ARTISTS + artistToDelete.getId())
                .then().statusCode(204);
        log.info("Artist with id {} and name {} was deleted", artistToDelete.getId(), artistToDelete.getName());
    }

    @Test
    public void deleteArtistWithoutAuthorizationTest() {
        List<Artist> artists = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ARTISTS)
                .body().as(new TypeRef<List<Artist>>() {
                });
        Artist artistToDelete = artists.stream()
                .filter(artist -> artist.getName() != null && artist.getName().startsWith("AT_"))
                .findFirst().orElse(null);
        ValidatableResponse response = given()
                .contentType(ContentType.JSON)
                .delete(BASE_URL + API + ARTISTS + artistToDelete.getId())
                .then().statusCode(401);
    }

    @Test
    public void deleteArtistAsNotAdminTest() {
        List<Artist> artists = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ARTISTS)
                .body().as(new TypeRef<List<Artist>>() {
                });
        Artist artistToDelete = artists.stream()
                .filter(artist -> artist.getName() != null && artist.getName().startsWith("AT_"))
                .findFirst().orElse(null);
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .delete(BASE_URL + API + ARTISTS + artistToDelete.getId())
                .then().statusCode(403);
    }

    @Test
    public void deleteInvalidArtistTest() {
        ValidatableResponse response = authenticatedAsAdminRequest()
                .delete(BASE_URL + API + ARTISTS + 0)
                .then().statusCode(404);
    }
}
