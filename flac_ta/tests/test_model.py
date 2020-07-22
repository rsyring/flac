# from flac_ta import model as m


# class TestPost:

#     def test_insert(self, mixer):
#         m.Post.testing_create()
#         assert m.Post.query.count() == 1


# class TestComment:

#     def test_insert(self, mixer):
#         mixer.blend(m.Comment)
#         assert m.Comment.query.count() == 1
#         comment = m.Comment.query.one()
#         print(comment)
#         print(comment.post)

#     def test_count(self, mixer):
#         m.Post.query.delete()
#         mixer.blend(m.Comment)
#         assert m.Comment.query.count() == 1
