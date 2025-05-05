package api.tests;

import api.model.Album;
import api.model.AlbumModel;
import io.restassured.common.mapper.TypeRef;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import io.restassured.response.ValidatableResponse;
import io.restassured.specification.RequestSpecification;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.Test;
import utils.TestDataUtils;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static api.endpoints.Endpoints.*;
import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static utils.TestDataUtils.*;

@Log4j2
public class AlbumsTests extends BaseTest {

    private AlbumModel album = new AlbumModel(getGeneratedName(), getRandomYear(), TestDataUtils.MusicGenre.ROCK.getValue(),
            getRandomPositiveInt(), getRandomPositiveInt(), 5);
    private AlbumModel albumForUpdate = new AlbumModel("updated", 2025, TestDataUtils.MusicGenre.ROCK.getValue(),
            214, 552, 5);
    private Map<String, Object> queryParams = TestDataUtils.createAlbumQueryParams(
            0, 20, "AT_", "ROCK", 1.0, 1000.0, "price_asc"
    );

    @Test
    public void createNewAlbumTest() {
        Album newAlbum = authenticatedAsAdminRequest()
                .body(album)
                .when()
                .post(BASE_URL + API + ALBUMS)
                .then().statusCode(201)
                .extract().as(Album.class);
        assertEquals(album.getTitle(), newAlbum.getTitle(), "The Title of created artist is incorrect");
        assertEquals(album.getArtist_id(), newAlbum.getArtist().getId(), "The description of created artist is incorrect");
        log.info("Album with id {} and name {} was created", newAlbum.getId(), newAlbum.getTitle());
    }

    @Test
    public void createNewAlbumWithoutAuthorizationTest() {
        ValidatableResponse response = given()
                .contentType(ContentType.JSON)
                .body(album)
                .when()
                .post(BASE_URL + API + ALBUMS)
                .then().statusCode(401);
    }

    @Test
    public void createNewAlbumAsNotAdminTest() {
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .body(album)
                .when()
                .post(BASE_URL + API + ALBUMS)
                .then().statusCode(403);
    }

    @Test
    public void createNewAlbumWithInvalidDataTest() {
        AlbumModel albumWithEmptyData = new AlbumModel("", 0, TestDataUtils.MusicGenre.ROCK.getValue(),
                getRandomPositiveInt(), getRandomPositiveInt(), 5);
        ValidatableResponse response = authenticatedAsAdminRequest()
                .body(albumWithEmptyData)
                .when()
                .post(BASE_URL + API + ALBUMS)
                .then().statusCode(422);
    }

    @Test
    public void getListOfAlbumsTest() {
        RequestSpecification request = authenticatedAsAdminRequest();
        queryParams.forEach(request::queryParam);

        List<Album> albums = request
                .when()
                .get(BASE_URL + API + ALBUMS)
                .then().statusCode(200)
                .extract().as(new TypeRef<List<Album>>() {
                });

        assertFalse(albums.isEmpty(), "Filtered artist list is empty");
        log.info("The list of artists is: {}",
                albums.stream()
                        .map(artist -> String.format("Name: %s, Release year: %s", album.getTitle(), album.getRelease_year()))
                        .collect(Collectors.joining("; ")));
    }

    @Test
    public void getListOfAlbumsWithoutAuthorizationTest() {
        RequestSpecification request = given();
        queryParams.forEach(request::queryParam);
        ValidatableResponse response = request
                .when()
                .get(BASE_URL + API + ALBUMS)
                .then().statusCode(401);
    }

    @Test
    public void getListOfAlbumsAsUserWithoutAdminRightsTest() {
        RequestSpecification request = authenticatedAsNotAdminRequest();
        request = authenticatedAsAdminRequest();
        queryParams.forEach(request::queryParam);

        List<Album> albums = request
                .when()
                .get(BASE_URL + API + ALBUMS)
                .then().statusCode(200)
                .extract().as(new TypeRef<List<Album>>() {
                });

        assertFalse(albums.isEmpty(), "Filtered artist list is empty");
        log.info("The list of artists is: {}",
                albums.stream()
                        .map(artist -> String.format("Name: %s, Release year: %s", album.getTitle(), album.getRelease_year()))
                        .collect(Collectors.joining("; ")));
    }

    @Test
    public void getAlbumByIdTest() {
        Album albumTest = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ALBUMS + "3")
                .then().statusCode(200)
                .extract().as(Album.class);
        assertEquals("test", albumTest.getTitle(), "The title of album is incorrect");
        log.info("Album with title {} was found", albumTest.getTitle());
    }

    @Test
    public void getAlbumByInvalidIdTest() {
        ValidatableResponse response = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ALBUMS + "0")
                .then().statusCode(404);
    }

    @Test
    public void getAlbumAsNoAuthorizedTest() {
        ValidatableResponse response = given()
                .when()
                .get(BASE_URL + API + ALBUMS + "3")
                .then().statusCode(401);
    }

    @Test
    public void getAlbumAsUserWithoutAdminRightsTest() {
        Album albumTest = authenticatedAsNotAdminRequest()
                .when()
                .get(BASE_URL + API + ALBUMS + "3")
                .then().statusCode(200)
                .extract().as(Album.class);
        assertEquals("test", albumTest.getTitle(), "The title of album is incorrect");
        log.info("Album with title {} was found", albumTest.getTitle());
    }

    @Test
    public void updateAlbumTest() {
        Album updatedAlbum = authenticatedAsAdminRequest()
                .body(albumForUpdate)
                .when()
                .put(BASE_URL + API + ALBUMS + 3)
                .then().statusCode(200)
                .extract().as(Album.class);
        log.info("Album's title after update is: {}", updatedAlbum.getTitle());
        assertEquals(albumForUpdate.getTitle(), updatedAlbum.getTitle(), "The title of updated album is incorrect");
        // return previous data
        albumForUpdate.setTitle("test");
        Response response = authenticatedAsAdminRequest()
                .body(albumForUpdate)
                .when()
                .put(BASE_URL + API + ALBUMS + 3);
        response.then().statusCode(200);
    }

    @Test
    public void updateAlbumWithoutAuthorizationTest() {
        ValidatableResponse response = given()
                .contentType(ContentType.JSON)
                .body(albumForUpdate)
                .when()
                .put(BASE_URL + API + ALBUMS + 3)
                .then().statusCode(401);
    }

    @Test
    public void updateAlbumAsNotAminTest() {
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .body(albumForUpdate)
                .when()
                .put(BASE_URL + API + ALBUMS + 3)
                .then().statusCode(403);
    }

    @Test
    public void updateInvalidAlbumTest() {
        ValidatableResponse response = authenticatedAsAdminRequest()
                .body(albumForUpdate)
                .when()
                .put(BASE_URL + API + ALBUMS + 0)
                .then().statusCode(404);
    }

    @Test
    public void updateAlbumWithInvalidDataTest() {
        AlbumModel albumForUpdate = new AlbumModel("", 2025, TestDataUtils.MusicGenre.ROCK.getValue(),
                214, 552, 5);
        ValidatableResponse response = authenticatedAsAdminRequest()
                .body(albumForUpdate)
                .when()
                .put(BASE_URL + API + ALBUMS + 3)
                .then().statusCode(422);
    }

    @Test
    public void deleteAlbumTest() {
        List<Album> albums = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ALBUMS)
                .body().as(new TypeRef<List<Album>>() {
                });
        Album albumToDelete = albums.stream()
                .filter(album -> album.getTitle() != null && album.getTitle().startsWith("AT_"))
                .findFirst().orElse(null);
        ValidatableResponse response = authenticatedAsAdminRequest()
                .delete(BASE_URL + API + ALBUMS + albumToDelete.getId())
                .then().statusCode(204);
        log.info("Album with id {} and name {} was deleted", albumToDelete.getId(), albumToDelete.getTitle());
    }

    @Test
    public void deleteAlbumWithoutAuthorizationTest() {
        List<Album> albums = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ALBUMS)
                .body().as(new TypeRef<List<Album>>() {
                });
        Album albumToDelete = albums.stream()
                .filter(album -> album.getTitle() != null && album.getTitle().startsWith("AT_"))
                .findFirst().orElse(null);
        ValidatableResponse response = given()
                .delete(BASE_URL + API + ALBUMS + albumToDelete.getId())
                .then().statusCode(401);
    }

    @Test
    public void deleteAlbumAsNotAdminTest() {
        List<Album> albums = authenticatedAsAdminRequest()
                .when()
                .get(BASE_URL + API + ALBUMS)
                .body().as(new TypeRef<List<Album>>() {
                });
        Album albumToDelete = albums.stream()
                .filter(album -> album.getTitle() != null && album.getTitle().startsWith("AT_"))
                .findFirst().orElse(null);
        ValidatableResponse response = authenticatedAsNotAdminRequest()
                .delete(BASE_URL + API + ALBUMS + albumToDelete.getId())
                .then().statusCode(403);
    }

    @Test
    public void deleteInvalidAlbumTest() {
        ValidatableResponse response = authenticatedAsAdminRequest()
                .delete(BASE_URL + API + ALBUMS + 0)
                .then().statusCode(404);
    }
}
