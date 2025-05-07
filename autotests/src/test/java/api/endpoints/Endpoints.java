package api.endpoints;

public class Endpoints {

    public static final String BASE_URL = "http://localhost:8000";
    public static final String API = "/api";
    public static final String AUTH = "/auth";
    public static final String REGISTER = AUTH + "/register";
    public static final String TOKEN = AUTH + "/token";
    public static final String ARTISTS = "/artists/";
    public static final String ALBUMS = "/albums/";
    public static final String USERS_USERNAME_RIGHTS = AUTH + "/users/%s/rights";
}
