#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-documentaries.jarbasai=skill_documentaries:DocumentariesSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-documentaries',
    version='0.0.1',
    description='ovos documentaries skill plugin',
    url='https://github.com/JarbasSkills/skill-documentaries',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_documentaries": ""},
    package_data={'skill_documentaries': ['locale/*', 'ui/*']},
    packages=['skill_documentaries'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
