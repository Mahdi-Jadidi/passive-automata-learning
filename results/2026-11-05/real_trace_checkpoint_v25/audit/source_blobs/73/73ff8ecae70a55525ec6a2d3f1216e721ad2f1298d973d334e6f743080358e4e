"""Exact experimental selected-output final-block cover, at most eight types."""
from collections import deque
import math
import time

METHOD='C025-selected-output-final-block-cover-v1'
MODEL_VERSION='selected-output-v1'
DEPTHS=(0,1,2,4,8,'full')
class Halt(Exception):pass
class BadInput(Exception):pass

def solve(data, *, depth, model_version, known_k=None, deadline=None):
    started=time.perf_counter()
    metrics=dict(search_nodes=0,complete_candidates=0,block_masks_computed=0,block_cache_hits=0,
                 validation_events=0,block_scan_events=0,local_events=0,trie_nodes=0)
    base=dict(schema_version=1,method=METHOD,model_version=model_version,depth=depth,known_k=known_k,metrics=metrics,
              assumptions=['only active owner emits current output','outcomes are not history inputs',
                           'common empty context at each declared trace start','finite observed consistency only'],
              protected_metadata_read=False)
    def poll():
        if deadline is not None and time.perf_counter()>=deadline:raise Halt('deadline')
    def emit(status,**fields):
        poll()
        return dict(base,status=status,complete=True,**fields)
    try:
        if deadline is not None and (type(deadline) not in (int,float) or type(deadline) is float and not math.isfinite(deadline)):
            raise BadInput('deadline must be finite absolute perf_counter time or None')
        poll()
        if model_version!=MODEL_VERSION:raise BadInput('explicit model_version selected-output-v1 required')
        if type(depth) not in (int,str) or depth not in DEPTHS:raise BadInput('depth must be 0,1,2,4,8 or full')
        if not isinstance(data,dict) or set(data)!={'alphabet','traces'}:raise BadInput('exact alphabet,traces schema required')
        alphabet=data['alphabet']
        if not isinstance(alphabet,list) or not 1<=len(alphabet)<=8:raise BadInput('alphabet must have 1..8 atomic IDs; selection is caller-owned')
        seen=set()
        for symbol in alphabet:
            poll()
            if not isinstance(symbol,str) or not symbol or symbol in seen:raise BadInput('IDs must be distinct nonempty strings')
            seen.add(symbol)
        alphabet=sorted(alphabet);m=len(alphabet)
        if known_k is not None and (type(known_k) is not int or not 1<=known_k<=m):raise BadInput('known_k must be an external integer in 1..m')
        if not isinstance(data['traces'],list):raise BadInput('traces must be list')
        file_ids=set()
        for trace in data['traces']:
            poll()
            if not isinstance(trace,dict) or set(trace)!={'file_id','events'}:raise BadInput('trace requires exactly file_id,events')
            fid=trace['file_id']
            if type(fid) is not int or fid in file_ids:raise BadInput('file_id must be unique integer')
            file_ids.add(fid)
            if not isinstance(trace['events'],list):raise BadInput('events must be list')
            for event in trace['events']:
                poll();metrics['validation_events']+=1
                if not isinstance(event,dict) or set(event)!={'id','outcome'}:raise BadInput('event requires exactly id,outcome')
                if not isinstance(event['id'],str) or event['id'] not in seen:raise BadInput('undeclared event ID')
                if event['outcome'] is not None and type(event['outcome']) is not bool:raise BadInput('outcome must be bool or None')

        cache={}
        def symbols(mask):
            return [a for i,a in enumerate(alphabet) if mask>>i&1]
        def block(mask):
            poll()
            if mask in cache:
                metrics['block_cache_hits']+=1;return cache[mask]
            metrics['block_masks_computed']+=1
            allowed=set(symbols(mask));records={};transitions={};known=unknown=local=0
            conflict=None
            # Adapted from tested C017 evaluate_block: exact shared trie IDs for
            # full histories; finite suffix key is (prior local IDs,current).
            for trace in data['traces']:
                poll();history=deque(maxlen=depth if depth!='full' else 0);prefix=0
                for ei,event in enumerate(trace['events']):
                    poll();metrics['block_scan_events']+=1
                    current=event['id']
                    if current not in allowed:continue
                    local+=1;metrics['local_events']+=1
                    if depth=='full':
                        transition=(prefix,current)
                        if transition not in transitions:
                            transitions[transition]=len(transitions)+1;metrics['trie_nodes']+=1
                        context=transitions[transition];prefix=context
                    else:context=(tuple(history),current)
                    reference=dict(file_id=trace['file_id'],event_index=ei)
                    y=event['outcome']
                    if y is None:unknown+=1
                    else:
                        known+=1
                        if context not in records:records[context]=(y,reference)
                        elif records[context][0]!=y:
                            conflict=dict(first=records[context][1],first_outcome=records[context][0],
                                          opposite=reference,opposite_outcome=y,current_id=current)
                            break
                    if depth!='full':history.append(current)
                if conflict is not None:break
            result=dict(mask=mask,blocks_symbols=symbols(mask),consistent=conflict is None,
                        labelled_contexts=len(records),local_events_scanned=local,known_events_scanned=known,
                        unknown_events_scanned=unknown,full_trie_nodes=len(transitions),conflict=conflict)
            cache[mask]=result;return result

        solutions=[]
        def witness(masks):
            # Replay every compatible block with exact context->output functions.
            functions=[]
            for mask in masks:
                poll();allowed=set(symbols(mask));records={};transitions={}
                for trace in data['traces']:
                    poll();history=deque(maxlen=depth if depth!='full' else 0);prefix=0
                    for ei,event in enumerate(trace['events']):
                        poll();current=event['id']
                        if current not in allowed:continue
                        if depth=='full':
                            transition=(prefix,current)
                            if transition not in transitions:transitions[transition]=len(transitions)+1
                            context=transitions[transition];prefix=context
                        else:context=(tuple(history),current)
                        y=event['outcome']
                        if y is not None:
                            if context in records:assert records[context]['outcome']==y
                            else:records[context]=dict(context=context,outcome=y,reference=dict(file_id=trace['file_id'],event_index=ei))
                        if depth!='full':history.append(current)
                trie=[]
                for (parent,current),node in transitions.items():
                    poll();trie.append(dict(parent=parent,event_id=current,node=node))
                rules=[]
                for rule in records.values():poll();rules.append(rule)
                functions.append(dict(block=symbols(mask),output_rules=rules,trie=trie,unspecified_outputs='arbitrary',
                                      unseen_extensions='arbitrary fallback; not a prediction rule'))
            return dict(blocks=[symbols(mask) for mask in masks],functions=functions)

        def cover(remaining,masks):
            poll();metrics['search_nodes']+=1
            if len(solutions)==2:return
            if known_k is not None and (len(masks)>known_k or len(masks)+remaining.bit_count()<known_k):return
            if not remaining:
                if known_k is None or len(masks)==known_k:
                    metrics['complete_candidates']+=1;solutions.append(witness(masks))
                return
            if known_k is not None and len(masks)==known_k:return
            anchor=remaining&-remaining;rest=remaining^anchor;sub=rest
            while True:
                poll();candidate=anchor|sub
                if block(candidate)['consistent']:cover(remaining^candidate,masks+[candidate])
                if len(solutions)==2:return
                if sub==0:break
                sub=(sub-1)&rest
        cover((1<<m)-1,[])
        checked=[]
        for item in cache.values():poll();checked.append(item)
        proof=dict(route='canonical_final_block_exact_cover',search_exhausted=len(solutions)<2,
                   block_checks=checked,enumeration='least remaining symbol anchored in each finalized block')
        if len(solutions)==2:return emit('ambiguous',alternatives=solutions,certificate=proof)
        if len(solutions)==1:return emit('certified_unique',partition=solutions[0]['blocks'],witness=solutions[0],certificate=proof)
        return emit('incompatible',certificate=proof)
    except BadInput as exc:
        return dict(base,status='invalid_input',complete=False,error=str(exc))
    except (Halt,KeyboardInterrupt,RecursionError,MemoryError) as exc:
        return dict(base,status='unresolved',complete=False,reason=type(exc).__name__)
    finally:metrics['solver_seconds']=time.perf_counter()-started
