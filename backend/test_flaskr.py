import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get("/api/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_category_not_found(self):
        res = self.client().get('/api/categories/1', json={'question': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_paginated(self):
        res = self.client().get("/api/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test__request_beyond_valid_page(self):
        res = self.client().get(
            '/api/questions?page=1000', json={'question': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_new_question(self):
        new_question = {
            'question': 'When was the fall of the berlin wall',
            'answer': '1989',
            'difficulty': '3',
            'category': 4
        }
        res = self.client().post("/api/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['question'], new_question['question'])
        self.assertEqual(data['category'], new_question['category'])

    def test_422_on_add_new_question(self):
        new_question = {
            'category': 'asd'
        }
        res = self.client().post('/api/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_404_on_add_new_question(self):
        new_question = {
            'category': 'asd'
        }
        res = self.client().get('/api/', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        question = Question.query.limit(1).one_or_none()

        res = self.client().delete("/api/questions/" + str(question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question.id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue('questions', None)

    def test_404_on_delete_unknown_question(self):
        res = self.client().delete('/api/questions/999999999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_422_on_delete_question(self):
        res = self.client().delete('/api/questions/aasdasdasd')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_question(self):
        search = {
            'searchTerm': 'a',
        }
        res = self.client().post("/api/search/questions", json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['total_questions'] > 0)

    def test_questions_by_category(self):
        res = self.client().get('/api/categories/Science/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['currentCategory'])

    def test_404_on_questions_by_category(self):
        res = self.client().get('/api/categories/marine/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_play_question(self):
        play = {
            "previous_questions": [],
            "quiz_category": {
                "id": 1
            }
        }
        res = self.client().post('/api/quizzes', json=play)
        first = json.loads(res.data)

        # {'question': {'answer': 'Alexander Fleming', 'category': 1, 'difficulty': 3, 'id': 21, 'question': 'Who discovered penicillin?'}}
        self.assertEqual(res.status_code, 200)
        self.assertEqual(first['success'], True)
        self.assertTrue(first['question'])
        self.assertTrue(first['question']['id'])

        play = {
            "previous_questions": [first['question']['id']],
            "quiz_category": {
                "id": 1
            }
        }
        res = self.client().post('/api/quizzes', json=play)
        second = json.loads(res.data)

        self.assertNotEqual(second['question']['id'], first['question']['id'])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(second['success'], True)
        self.assertTrue(second['question'])

    def test_422_on_play_question(self):
        play = {
            "previous_questions": [],
            "quiz_category": "Science"
        }
        res = self.client().post('/api/quizzes', json=play)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
