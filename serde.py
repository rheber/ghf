'''(De)Serialisation.'''

from typing import Dict, Tuple

class GhfSerdeException(Exception):
    '''Custom exception.'''

def loadFollowees(path: str) -> Dict[str, str]:
    '''Dictionary of names and descriptions in followees file.'''

    def ud(line: str) -> Tuple[str, str]:
        '''Break line into user and description.'''
        sp = line.split('\t')
        if len(sp) == 0:
            return ('', '')
        if len(sp) == 1:
            return (sp[0], '')
        return (sp[0], sp[1])

    try:
        return {ud(line)[0]:ud(line)[1] for
                line in list(open(path).read().split('\n')) if line}
    except FileNotFoundError:
        with open(path, 'w') as fo:
            fo.write('')
        return {}
    except IndexError:
        raise GhfSerdeException('Error reading followees file.')
