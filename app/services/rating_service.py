from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..models.models import Rating, Album, User, RatingVote
from ..schemas.schemas import RatingCreate, AlbumRatingStats, UserRatingStats

class RatingService:
    """Сервис для работы с рейтингами и отзывами."""

    REVIEW_MIN_LENGTH = 10
    REVIEW_MAX_LENGTH = 2000
    MAX_RATING = 5
    MIN_RATING = 1

    @staticmethod
    def calculate_weighted_rating(
        rating: float,
        total_votes: int,
        verified_purchase: bool,
        review_quality: float,
        age_days: int
    ) -> float:
        """
        Вычисляет взвешенный рейтинг с учетом различных факторов.
        
        Args:
            rating: базовая оценка (1-5)
            total_votes: общее количество голосов за отзыв
            verified_purchase: является ли покупателем
            review_quality: качество отзыва (0-1)
            age_days: возраст отзыва в днях
        
        Returns:
            float: взвешенный рейтинг
            
        Raises:
            ValueError: если rating вне диапазона [1, 5]
        """
        if not RatingService.MIN_RATING <= rating <= RatingService.MAX_RATING:
            raise ValueError(f"Rating must be between {RatingService.MIN_RATING} and {RatingService.MAX_RATING}")
            
        # Базовый вес отзыва
        weight = 1.0
        
        # Увеличиваем вес для подтвержденных покупок
        if verified_purchase:
            weight *= 1.5
            
        # Учитываем количество голосов (больше голосов = больше вес)
        votes_weight = min(total_votes / 10.0, 2.0)  # Максимум удвоение веса
        weight *= (1.0 + votes_weight)
        
        # Учитываем качество отзыва
        weight *= (1.0 + review_quality)
        
        # Уменьшаем вес старых отзывов
        age_penalty = max(0.5, 1.0 - (age_days / 365))  # Максимальное снижение веса на 50%
        weight *= age_penalty
        
        return round(rating * weight, 2)

    @staticmethod
    def calculate_review_quality(helpful_votes: int, unhelpful_votes: int, text_length: int) -> float:
        """
        Вычисляет показатель качества отзыва.
        
        Args:
            helpful_votes: количество голосов "полезно"
            unhelpful_votes: количество голосов "бесполезно"
            text_length: длина текста отзыва
            
        Returns:
            float: значение от 0 до 1, где 1 = отличный отзыв
            
        Raises:
            ValueError: если голоса или длина текста отрицательные
        """
        if helpful_votes < 0 or unhelpful_votes < 0:
            raise ValueError("Votes cannot be negative")
        if text_length < 0:
            raise ValueError("Text length cannot be negative")
            
        # Оценка полезности от других пользователей
        total_votes = helpful_votes + unhelpful_votes
        if total_votes > 0:
            helpfulness = helpful_votes / total_votes
        else:
            helpfulness = 0.5  # Нейтральная оценка если нет голосов
            
        # Оценка длины отзыва
        length_score = 0.0
        if text_length > 0:
            if text_length < RatingService.REVIEW_MIN_LENGTH:
                length_score = text_length / RatingService.REVIEW_MIN_LENGTH
            elif text_length <= RatingService.REVIEW_MAX_LENGTH:
                length_score = 1.0
            else:
                length_score = RatingService.REVIEW_MAX_LENGTH / text_length
                
        # Общая оценка качества (70% полезность, 30% длина)
        return round((helpfulness * 0.7) + (length_score * 0.3), 2)

    @staticmethod
    def get_album_rating_stats(db: Session, album_id: int) -> AlbumRatingStats:
        """
        Получает статистику рейтинга для альбома.
        
        Args:
            db: сессия базы данных
            album_id: ID альбома
            
        Returns:
            AlbumRatingStats: статистика рейтингов альбома
            
        Raises:
            ValueError: если album_id отрицательный
        """
        if album_id < 1:
            raise ValueError("Album ID must be positive")
            
        # Получаем все рейтинги альбома
        ratings = db.query(Rating).filter(
            Rating.album_id == album_id
        ).all()
        
        if not ratings:
            return AlbumRatingStats(
                album_id=album_id,
                weighted_rating=0.0,
                rating_count=0,
                verified_rating_count=0,
                rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                verified_rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            )
            
        # Подсчет распределения оценок
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        verified_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        verified_count = 0
        weighted_sum = 0.0
        total_weight = 0.0
        
        for r in ratings:
            # Проверяем валидность оценки
            if not RatingService.MIN_RATING <= r.score <= RatingService.MAX_RATING:
                continue
                
            # Обновляем распределение
            distribution[r.score] = distribution.get(r.score, 0) + 1
            if r.is_verified_purchase:
                verified_distribution[r.score] = verified_distribution.get(r.score, 0) + 1
                verified_count += 1
                
            # Считаем взвешенный рейтинг
            age_days = (datetime.utcnow() - r.created_at).days
            quality = RatingService.calculate_review_quality(
                r.helpful_votes, 
                r.unhelpful_votes,
                r.review_text_length
            )
            weight = RatingService.calculate_weighted_rating(
                r.score,
                r.helpful_votes + r.unhelpful_votes,
                r.is_verified_purchase,
                quality,
                age_days
            )
            weighted_sum += weight
            total_weight += 1
            
        weighted_rating = weighted_sum / total_weight if total_weight > 0 else 0
            
        return AlbumRatingStats(
            album_id=album_id,
            weighted_rating=round(weighted_rating, 2),
            rating_count=len(ratings),
            verified_rating_count=verified_count,
            rating_distribution=distribution,
            verified_rating_distribution=verified_distribution
        )

    @staticmethod
    def get_user_rating_stats(db: Session, user_id: int) -> UserRatingStats:
        """
        Получает статистику рейтингов пользователя.
        
        Args:
            db: сессия базы данных
            user_id: ID пользователя
            
        Returns:
            UserRatingStats: статистика рейтингов пользователя
            
        Raises:
            ValueError: если user_id отрицательный
        """
        if user_id < 1:
            raise ValueError("User ID must be positive")
            
        # Получаем все рейтинги пользователя с оптимизированным запросом
        ratings = db.query(Rating).filter(
            Rating.user_id == user_id
        ).all()
        
        if not ratings:
            return UserRatingStats(
                user_id=user_id,
                total_ratings=0,
                average_rating=0.0,
                rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                helpful_votes_received=0,
                total_review_length=0
            )
            
        # Подсчет статистики
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        total_score = 0
        total_helpful_votes = 0
        total_length = 0
        valid_ratings = 0
        
        for r in ratings:
            # Проверяем валидность оценки
            if not RatingService.MIN_RATING <= r.score <= RatingService.MAX_RATING:
                continue
                
            distribution[r.score] = distribution.get(r.score, 0) + 1
            total_score += r.score
            total_helpful_votes += r.helpful_votes
            total_length += r.review_text_length
            valid_ratings += 1
            
        average_rating = round(total_score / valid_ratings, 2) if valid_ratings > 0 else 0.0
            
        return UserRatingStats(
            user_id=user_id,
            total_ratings=valid_ratings,
            average_rating=average_rating,
            rating_distribution=distribution,
            helpful_votes_received=total_helpful_votes,
            total_review_length=total_length
        )

    @staticmethod
    def update_album_rating(db: Session, album_id: int) -> None:
        """
        Обновляет рейтинг альбома на основе всех отзывов.
        
        Args:
            db: сессия базы данных
            album_id: ID альбома
            
        Raises:
            ValueError: если album_id отрицательный
        """
        if album_id < 1:
            raise ValueError("Album ID must be positive")
            
        stats = RatingService.get_album_rating_stats(db, album_id)
        
        # Обновляем информацию в БД с оптимистичной блокировкой
        album = db.query(Album).filter(Album.id == album_id).with_for_update().first()
        if album:
            album.weighted_rating = stats.weighted_rating
            album.rating_count = stats.rating_count
            album.verified_rating_count = stats.verified_rating_count
            db.commit()
