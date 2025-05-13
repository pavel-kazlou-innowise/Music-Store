package utils;

import org.apache.commons.lang3.RandomStringUtils;

import java.time.Year;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

public class TestDataUtils {

    public static String getGeneratedEmail() {
        return STR."\{RandomStringUtils.randomAlphanumeric(10, 15)}@\{RandomStringUtils.randomAlphabetic(4, 8)}.\{RandomStringUtils.randomAlphabetic(2, 3)}";
    }

    public static String getGeneratedName() {
        return STR."AT_Name_\{RandomStringUtils.randomAlphabetic(10)}";
    }

    public static String getGeneratedString() {
        return RandomStringUtils.randomAlphabetic(8);
    }

    public static int getRandomYear() {
        int currentYear = Year.now().getValue();
        return ThreadLocalRandom.current().nextInt(1900, currentYear + 1);
    }

    public static String getGeneratedDescription() {
        return STR."AT_Description_\{RandomStringUtils.randomAlphabetic(10)}";
    }

    public static int getRandomPositiveInt() {
        return ThreadLocalRandom.current().nextInt(0, 1000);
    }

    public static Map<String, Object> createAlbumQueryParams(
            Integer skip,
            Integer limit,
            String search,
            String genre,
            Double minPrice,
            Double maxPrice,
            String sortBy
    ) {
        Map<String, Object> params = new HashMap<>();
        if (skip != null) params.put("skip", skip);
        if (limit != null) params.put("limit", limit);
        if (search != null && !search.isEmpty()) params.put("search", search);
        if (genre != null && !genre.isEmpty()) params.put("genre", genre);
        if (minPrice != null) params.put("min_price", minPrice);
        if (maxPrice != null) params.put("max_price", maxPrice);
        if (sortBy != null && !sortBy.isEmpty()) params.put("sort_by", sortBy);
        return params;
    }

    public static enum MusicGenre {
        ROCK,
        POP,
        JAZZ,
        HIP_HOP,
        CLASSICAL,
        ELECTRONIC,
        COUNTRY,
        REGGAE,
        METAL,
        BLUES;

        public String getValue() {
            return this.name(); // returns enum value as String
        }
    }
}
