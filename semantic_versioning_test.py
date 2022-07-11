import unittest 
# how to use: "python -m unittest semver/semantic_versioning_test.py" in cmd

import re
# import the file and all modules in it
import semver.maven_semantic_versioning as semantic_versioning

class TestMavenSemanticVersioning(unittest.TestCase):
    def setUp(self):
        self.semver = semantic_versioning.SemanticVersioning()
         
        # works for keywords:
        # self.major = "major"
        # self.minor = "minor"
        # self.patch = "fix"
        
        self.major = self.semver.major
        self.minor = self.semver.minor
        self.patch = self.semver.patch
        
        # collected via gh Actions 
        # ':' is missing so missing keyword
        self.missing_keyword = [f"{self.patch}(small fixes)"] 
        # squashed and merged by gh
        self.squashed_commits = [f"""Unittests (#6)
                        * {self.patch}(test): small test additions
                        * {self.minor}(test): literally testing with unittest
                        * {self.major}(restructure): code restructured
                        * {self.patch}(added some tests): tests
                        * {self.minor}(restructured): restructured code""",
                        f"{self.patch}(small fixes)"] 
        self.squashed_commits_keywords = [
            self.patch, self.minor, self.major, self.patch, self.minor]
        
        
        # all data related to patch releases
        # 3 patch matches
        self.patch_1 = [f"{self.patch}(test): test", 
                        f"{self.patch}(test1): test1", 
                        f"{self.patch}(test2): test2"]
        # only one commit feasable
        self.patch_2 = [f"{self.patch}(test): test", 
                        f"{self.patch}():", 
                        f"{self.patch}(test2) test2"]
        # only one commit
        self.patch_3 = [f"{self.patch}(test): test"]
        
        self.patch_1_keywords = [self.patch, self.patch, self.patch]
        self.patch_2_keywords = [self.patch] 
        self.patch_3_keywords = [self.patch]
        
        
        # all data related to minor releases
        # 1 minor 2 patch
        self.minor_1 = [f"{self.patch}(test): test", 
                        f"{self.minor}(minor): test1", 
                        f"{self.patch}(test2): test2"]
        # only one commit feasable
        self.minor_2 = [f"{self.minor}(test): test", 
                        f"{self.patch}():", 
                        f"{self.patch}(test2) test2"]
        # only one commit
        self.minor_3 = [f"{self.patch}(minor): test"]
        
        self.minor_1_keywords = [self.patch, self.minor, self.patch]
        self.minor_2_keywords = [self.minor] 
        self.minor_3_keywords = [self.patch]
        
        
        # all data related to major releases
        # 1 major 1 minor 1 patch
        self.major_1 = [f"{self.patch}(test): test", 
                        f"{self.minor}(minor): test1", 
                        f"{self.major}(test2): test2"]
        # only one commit feasable
        self.major_2 = [f"{self.major}(test): test", 
                        f"{self.patch}():", 
                        f"{self.major}(test2) test2"]
        # only one commit
        self.major_3 = [f"{self.major}(minor): test"]
        
        self.major_1_keywords = [self.patch, self.minor, self.major]
        self.major_2_keywords = [self.major] 
        self.major_3_keywords = [self.major]
        
        # testing regex
        self.regex = [
            f"{self.patch}({self.minor}({self.major}" +
            "(deep): test): test): test"]
        self.regex_keywords = [self.patch]
        
        
        
        
    
    # sees if the version number matches the Semver format    
    def test_get_version(self):
        self.assertTrue(re.match(r"[0-9]+\.[0-9]+\.[0-9]+",
                                 self.semver.get_version()))

    # tests if new version is set properly
    def test_set_version(self):
        original_version = self.semver.get_version() 
        self.semver.set_version("1.0.0")
        self.assertEqual("1.0.0", self.semver.get_version())
        # to undo the changes to the pom
        self.semver.set_version(original_version)
    
    def test_modify_version_number_major(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        updated_version = self.semver.modify_version_number(self.semver.major)
        self.assertEqual("2.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_modify_version_number_minor(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        updated_version = self.semver.modify_version_number(self.semver.minor)
        self.assertEqual("1.1.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_modify_version_number_patch(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        updated_version = self.semver.modify_version_number(self.semver.patch)
        self.assertEqual("1.0.1", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_modify_version_number_major_snapshot(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0-SNAPSHOT")
        updated_version = self.semver.modify_version_number(self.semver.major)
        self.assertEqual("1.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_modify_version_number_minor_snapshot(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0-SNAPSHOT")
        updated_version = self.semver.modify_version_number(self.semver.minor)
        self.assertEqual("1.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_modify_version_number_patch_snapshot(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0-SNAPSHOT")
        updated_version = self.semver.modify_version_number(self.semver.patch)
        self.assertEqual("1.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_modify_version_number_version_none(self):
        original_version = self.semver.get_version()
        self.semver.set_version(None)
        self.assertRaises(
            TypeError,
            self.semver.modify_version_number, 
            version_type=self.semver.patch)
        self.semver.set_version(original_version)
    
    def test_modify_version_number_no_version_string(self):
        original_version = self.semver.get_version()
        self.semver.set_version("")
        self.assertRaises(
            ValueError,
            self.semver.modify_version_number, 
            version_type=self.semver.patch)
        self.semver.set_version(original_version)
    
    def test_modify_version_number_random_string(self):
        original_version = self.semver.get_version()
        self.semver.set_version("ffygxffd.g54s,")
        self.assertRaises(
            ValueError,
            self.semver.modify_version_number, 
            version_type=self.semver.patch)
        self.semver.set_version(original_version)
        
    # should never contain a skip ci commit
    def test_get_commits_til_tag(self):
        # if used properly it should always contain an empty list
        # if not it should be by human error
        commits = self.semver.get_commits_til_tag()
        # to test this well look wether the [skip ci] flag is 
        for commit in commits:
            self.assertNotIn("[skip semVer]", commit)
            
    def test_analyze_git_commits_no_match(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.missing_keyword), 
            []
        )
    
    def test_analyze_git_commits_no_commits(self):
        self.assertListEqual(
            self.semver.analyze_git_commits([]), 
            []
        )
    
    def test_analyze_git_commits_multiple_matches(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.squashed_commits), 
            self.squashed_commits_keywords
        )
        
    def test_analyze_git_commits_patch_1(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.patch_1), 
            self.patch_1_keywords
        )
    
    def test_analyze_git_commits_patch_2(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.patch_2), 
            self.patch_2_keywords
        )
    
    def test_analyze_git_commits_patch_3(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.patch_3), 
            self.patch_3_keywords
        )
    
    def test_analyze_git_commits_minor_1(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.minor_1), 
            self.minor_1_keywords
        )
    
    def test_analyze_git_commits_minor_2(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.minor_2), 
            self.minor_2_keywords
        )
    
    def test_analyze_git_commits_minor_3(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.minor_3), 
            self.minor_3_keywords
        )
    
    def test_analyze_git_commits_major_1(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.major_1), 
            self.major_1_keywords
        )
    
    def test_analyze_git_commits_major_2(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.major_2), 
            self.major_2_keywords
        )
    
    def test_analyze_git_commits_major_3(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.major_3), 
            self.major_3_keywords
        )
    
    def test_analyze_git_commits_regex_1(self):
        self.assertListEqual(
            self.semver.analyze_git_commits(self.regex), 
            self.regex_keywords
        )
        
    def test_analyze_git_commits_regex_2(self):
        self.assertNotIn(
            self.major,
            self.semver.analyze_git_commits(self.regex)
        )
    
    def test_analyze_git_commits_regex_3(self):
        self.assertNotIn(
            self.minor,
            self.semver.analyze_git_commits(self.regex)
        )
            
    def test_get_version_type_regex_1(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.regex_keywords), 
            self.patch
        )
    
    def test_get_version_type_regex_2(self):
        self.assertNotEqual(
            self.semver.get_highest_version_type(self.regex_keywords), 
            self.major
        )
    
    def test_get_version_type_patch_1(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.patch_1_keywords), 
            self.patch
        )

    def test_get_version_type_patch_2(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.patch_2_keywords), 
            self.patch
        )
    
    def test_get_version_type_minor_1(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.minor_1_keywords), 
            self.minor
        )
    
    def test_get_version_type_minor_2(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.minor_2_keywords), 
            self.minor
        )
    
    def test_get_version_type_major_1(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.major_1_keywords), 
            self.major
        )

    def test_get_version_type_major_2(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.major_2_keywords), 
            self.major
        )
    
    def test_get_version_type_major_3(self):
        self.assertEqual(
            self.semver.get_highest_version_type(self.major_3_keywords), 
            self.major
        )    
    
        
    def test_update_version_no_match(self):
        self.assertRaises(
            semantic_versioning.MissingKeywordException, 
            self.semver.update_version, 
            commits=self.missing_keyword)
    
    def test_update_version_squashed_commits(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.squashed_commits)
        # major as highest keyword
        self.assertEqual("2.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_patch_1(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.patch_1)
        # major as highest keyword
        self.assertEqual("1.0.1", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_patch_2(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.patch_2)
        # major as highest keyword
        self.assertEqual("1.0.1", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_minor_1(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.minor_1)
        # major as highest keyword
        self.assertEqual("1.1.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_minor_2(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.minor_2)
        # major as highest keyword
        self.assertEqual("1.1.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_major_1(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.major_1)
        # major as highest keyword
        self.assertEqual("2.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_major_2(self):
        original_version = self.semver.get_version()
        self.semver.set_version("1.0.0")
        self.semver.update_version(self.major_2)
        # major as highest keyword
        self.assertEqual("2.0.0", self.semver.get_version())
        self.semver.set_version(original_version)
    
    def test_update_version_SNAPSHOT(self):
        original_version = self.semver.get_version()
        self.semver.set_version("3.23.454-SNAPSHOT")
        self.semver.update_version(self.minor_2)
        # major as highest keyword
        self.assertEqual("3.23.454", self.semver.get_version())
        self.semver.set_version(original_version)
        
if __name__ == "__main__":
    unittest.main()