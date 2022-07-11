"""
script for updating the version of a maven project based on git commits

Todo:
Nice to have:
    Release ordner mit Jar, Zip
    Release Notes
"""
# module accessing xml
import xml.etree.ElementTree as ET 
# regex for analyzing commit messages
import re
# accessing working directory
import os
# managing git repo
from git import Repo

class MissingKeywordException(Exception):
    """
    raised when no keyword is found in the commit messages
    """
    pass

class SemanticVersioning:
    def __init__(self):
        # set variables for the keywords, so they can be changed easily
        # MAJOR.MINOR.PATCH as seen on https://semver.org/
        self.major = "major"
        self.minor = "minor"
        self.patch = "fix"
        # flag used by the Actions Bot to mark an automated push
        # only change it, if you also change the flag produced by the 
        # GH Actions bot
        self.actionsbot_flag = "[skip semVer]"
        # git setup
        self.dirpath  = os.getcwd() # path of current working directory
        self.repo = Repo(self.dirpath) # git repo of current directory
        self.main = self.repo.branches.main 
        self.origin = self.repo.remotes.origin # remote loction of repo (github)
        # xml ET setup
        # register namespace before parsing --> otherwise multiple errors
        ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
        self.tree = ET.parse(f"{self.dirpath}/pom.xml") # pom xml tree
        self.root = self.tree.getroot() # root of xml tree

        # location of the version number in pom 
        self.version_location = self.root.find(
            "{http://maven.apache.org/POM/4.0.0}version")    
        
        
        
    def write_to_xml(self):
        """
        writes the current element tree on self.tree in pom.xml
        """
        self.tree.write("pom.xml", encoding="utf-8", xml_declaration=True)
        
    def set_version(self, new_version):
        """sets a new version and writes it to the pom.xml file

        Args:
            new_version (string): new version the pom should be updated to
        """
        # print to see, if version was updated correct
        # set the new version in the xml Element tree
        self.version_location.text = new_version
        self.write_to_xml() # write updated Element Tree to pom.xml
        # print to see, if version was updated correct
    
    def get_version(self):
        """returns the version number of the project

        Returns:
            string: version of the pom.xml
        """
        version = self.version_location.text
        return version
    
    def modify_version_number(self, version_type):
        """Changes the Version number based on the given version type

        Args:
            version_type (string): defines which version number should be 
            updated
        """
        # get version string
        version = self.get_version() 
        # check if the version number is a string
        if type(version) != str:
            raise TypeError("Version must be string type")
        # check if the version number fits the semver Specification
        if re.match(r"[0-9]+\.[0-9]+\.[0-9]+",version) == None:
            raise ValueError("Version must fit the SemVer Specifications")
        # split the version number in it's 3 components
        major_num, minor_num, patch_num = version.split('.')
        # match case for the version_type arg 
        # (Python Version of switch-Statement)
        # in case there is a SNAPSHOT Version
        if("SNAPSHOT" in patch_num):
            # only take the patch_number
            patch_num = patch_num.split("-")[0] 
        else: 
            match(version_type):
                # in case a Major Release is triggered
                case self.major:
                    # increase major number and set minor and patch number to 0
                    major_num = int(major_num)+1
                    minor_num = 0
                    patch_num = 0
                # in case a Minor Release is triggered
                case self.minor:
                    # increase minor number and set patch number to 0
                    minor_num = int(minor_num)+1
                    patch_num = 0
                # in case a Patch Release is triggered
                case self.patch: 
                    # increase patch number
                    patch_num = int(patch_num)+1
        # merge the version number together        
        version = f"{major_num}.{minor_num}.{patch_num}"
        # set the new version in pom
        self.set_version(version)
    
    def get_commits_til_tag(self):
        """returns all commits, until the skip ci flag is found
        skip ci is in commits pushed by GH Actions

        Returns:
            List(String): strings of multiple Commits
        """
        # gathers all commits
        commits = list(self.repo.iter_commits(rev=self.main))
        print("last commits: ")
        for i in range(len(commits)):
            # convert the commits to only read the message
            commits[i] = commits[i].message
            # if the flag used by the GH Actions Bot is found 
            if(self.actionsbot_flag in commits[i]):
                # Only Take commits pushed after the flag was found
                commits = commits[:i] 
                break   
            # print the commits chronologically (most recent first)
            print(f"{i}:", commits[i])
            
        return commits
    
    def analyze_git_commits(self, commits):
        """
        analyze git commits for keywords used to increase version number
        
        Args:
            commits List(string): strings of multiple Commits
            
        Returns:
            List(strings): List with keywords -> [keywords]
            
        Keywords for git commits:
            "fix(x): y"
            "minor(x): y"
            "major(x): y"
        
            where x is are brief keyword(s) describing the topic 
            or the ticket name and y is a more detailed text

        Examples:
            fix(GH Actions): fixed a small bug with Github actions
            minor(semver): added update_version function
            major(semver): removed and renamed multiple functions
        """
        
        matches = [] # create empty list for saving the matched strings
        for commit in commits: # for all commits
            # create a pattern using the chosen keywords
            # re.escape for the possibility to use special chars like 
            # '+' in the keyword
            pattern = r"((" + re.escape(self.patch) + r"|" + re.escape(
                self.minor) + r"|" + re.escape(self.major) + r")\(.+\):.+)"
            # look for the keywords in the commit messages and append them 
            # to the matches array
            matches += re.findall(pattern = pattern,
              string = commit, flags=re.MULTILINE)
        # get only the version types in a list
        version_types = map(lambda x: x[1], matches)
        version_types = list(version_types)
        return version_types
    
    def get_highest_version_type(self, version_types):
        """returns the highest version type in a list of Strings

        Args:
            version_types (List(String)): a list of version types

        Returns:
            string: the highest version type mentioned in the list
        """
        if(self.major in version_types):
            return self.major
        if(self.minor in version_types):
            return self.minor
        if(self.patch in version_types):
            return self.patch
     
    def update_version(self, commits): 
        """
        Call this method to update the version number.
        Glues the other Methods together.
        
        Args:
            commits List(string): strings of multiple Commits

        Raises:
            MissingKeywordException: if none of the keywords was used in the 
            last Commits this Exception will be raised
        """
        # get the list of Keywords
        version_types = self.analyze_git_commits(commits)
        # if the List is Empty
        if(version_types == []):
            # Raise the MissingKeywordException
            raise MissingKeywordException(
                "Please use the SemVer keywords in your Commit Messages")
        print(version_types)
        # saves the highest version_type metioned in commit messages 
        version_type = self.get_highest_version_type(version_types)
        
        # modyfy the version number based on the selected version type
        self.modify_version_number(version_type)
            
# if this file is executed
if __name__ == "__main__":
    # create a Semantic Versioning Object
    semver = SemanticVersioning()
    print(f"old version: {semver.get_version()}")
    # get commits
    commits = semver.get_commits_til_tag()
    # Updates the Version number
    semver.update_version(commits)
    print(f"new version: {semver.get_version()}")
    